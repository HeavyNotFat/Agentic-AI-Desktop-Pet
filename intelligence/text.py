import re
import json
import importlib
import typing

from . import translate
from . import external

import dashscope
import requests

memories = []
prompts = {}
with open("./resources/functions.json", "r", encoding="utf-8") as f:
    tools = json.load(f)
    tool_names = []
    properties = {}
    for tool in tools:
        tool_names.append(tool['function']['name'])
        properties.update({tool['function']['name']: list(tool['function']['parameters']['properties'].keys())})
    f.close()


def clear_memories():
    global memories
    memories = []
    for role, content in prompts.items():
        memories.append({"role": re.sub(r'\d+', '', role), "content": content})


def reload_api(api_key):
    dashscope.api_key = api_key


def reload_memories(model):
    global memories, prompts
    try:
        with open(f"./intelligence/prompts/{model}.json", "r", encoding="utf-8") as sf:
            prompts = json.load(sf)
            clear_memories()
            sf.close()
    except (FileNotFoundError, FileExistsError):
        memories = []
        prompts = {}


def reload_tools():
    global tools, tool_names, properties
    importlib.reload(external)
    with open("./resources/functions.json", "r", encoding="utf-8") as ff:
        tools = json.load(ff)
        tool_names = []
        properties = {}
        for tool in tools:
            tool_names.append(tool['function']['name'])
            properties.update({tool['function']['name']: list(tool['function']['parameters']['properties'].keys())})
        ff.close()


def TextGeneratorLocal(prompt, url, api_config):
    bodies = {}
    if api_config['text']['api']:
        bodies.update({api_config['text']['api']: api_config['text']['api-key']})
    if api_config['text']['model']:
        bodies.update({api_config['text']['model']: api_config['text']['model-name']})
    if api_config['text']['tools']:
        bodies.update({api_config['text']['tools']: tools})

    memories.append({"role": "user", "content": prompt})
    bodies.update({api_config['text']['messages']: memories})
    with requests.post(url, json=bodies, stream=True) as response:
        response.raise_for_status()
        history = ""
        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
            response_result = json.loads(chunk)
            keys = api_config['text']['endpoint'].split('.')
            for key in keys:
                if isinstance(response_result, dict) and key in response_result:
                    response_result = response_result[key]
            history += response_result
            yield history
        memories.append({'role': 'assistant', 'content': history})
    yield history


class TextGenerator:
    @staticmethod
    def get_response(extra_body, model, enable_tools: bool = True):
        if enable_tools:
            completion = dashscope.Generation().call(
                model=model,
                messages=memories,
                presence_penalty=0.6,
                extra_body=extra_body,
                stream=True,
                tools=tools
            )
        else:
            completion = dashscope.Generation().call(
                model=model,
                messages=memories,
                presence_penalty=0.6,
                stream=True,
                extra_body=extra_body
            )
        return completion

    def generate_text(self, prompt, model, language: typing.Literal['zh-Hans', 'en', 'ja', 'ko'] = "ja",
                      is_search_online: bool = False):
        def process_chunks(completion_, memories_, extra_body_, model_, external_):
            """
            递归函数

            用于循环检测工具调用
            """
            chunk_message = None
            for chunk in completion_:
                if chunk.status_code != 200:
                    yield (f"AI Answer failed to call: \n\n"
                           f"{chunk.message}\n\n{translate.machine_translate(chunk.message, language)}")
                    return
                chunk_message = chunk.output.choices[0].message

                if 'tool_calls' in chunk_message:
                    if chunk.output.choices[0].finish_reason == 'tool_calls':
                        memories_.append(chunk_message)
                        to_be_called_tool = chunk_message.tool_calls[0]['function']
                        tool_info = {"name": to_be_called_tool['name'], "role": "tool"}

                        compound_parameters = json.loads(to_be_called_tool['arguments'])
                        to_be_called_function = getattr(external_, to_be_called_tool['name'])
                        tool_info['content'] = to_be_called_function(**compound_parameters)
                        memories_.append(tool_info)

                        new_completion = self.get_response(extra_body_, model_)
                        yield from process_chunks(new_completion, memories_, extra_body_, model_, external_)
                        return
                else:
                    memories_.append(chunk_message)
                    if 'reasoning_content' in chunk_message.keys() and \
                            not chunk_message.content.strip() and chunk_message['reasoning_content'].strip():
                        yield f"<think>\n{chunk_message['reasoning_content']}\n</think>"
                    else:
                        yield chunk_message.content
            yield chunk_message.content

        extra_body = {}
        extra_body.update({"enable_search": is_search_online})
        memories.append({"role": "user", "content": prompt})
        completion = self.get_response(extra_body, model)
        yield from process_chunks(completion, memories, extra_body, model, external)


class CustomGenerator:
    def __init__(self, messages: list, is_translate, target_lang: str):
        self.messages = messages
        self.is_translate = is_translate
        self.target_lang = target_lang

    def generate_text(self):
        completion = dashscope.Generation().call(
            model="qwen-mt-turbo",
            messages=self.messages,
            translation_options={
                "source_lang": "Chinese",
                "target_lang": self.target_lang
            }
        )
        try:
            message = completion.output.choices[0].message.content
        except AttributeError:
            message = None
        self.messages.append({"role": "assistant", "content": message})
        return message
