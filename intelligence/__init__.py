import typing

from . import text
from . import recognition
from . import voice
from . import translate


def reload_api(ifly_api_id, ifly_api_key, ifly_api_secret, ali_api_key) -> None:
    recognition.API_ID = ifly_api_id
    recognition.API_KEY = ifly_api_key
    recognition.API_SECRET = ifly_api_secret

    text.reload_api(ali_api_key)


def load_gpt_sovits(url: str) -> dict:
    try:
        module_info = voice.get_module_lists(url)
    except __import__("requests").exceptions.ReadTimeout:
        module_info = {}
    return module_info


def text_generator(prompt, model, is_search_online: bool, api_config: dict,
                   language: typing.Literal['zh-Hans', 'en', 'ja', 'ko'] = "ja", url: str | None = None):
    if url is None:
        yield from text.TextGenerator().generate_text(prompt, model, language, is_search_online)
    else:
        yield from text.TextGeneratorLocal(prompt, url, api_config)
