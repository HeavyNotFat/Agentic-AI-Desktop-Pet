import time
import shutil
import os
import json
import locale
import random
import difflib
import typing


def logger(text: str, father_dir: str) -> None:
    """日志记录"""
    current_file = f"{father_dir}/{time.strftime('%Y-%m-%d')}.txt"
    if not os.path.exists(father_dir):
        os.mkdir(father_dir)
    if not os.path.isfile(current_file):
        open(current_file, "w", encoding="utf-8").close()
    with open(f"{current_file}", "a", encoding="utf-8") as f:
        f.write(f"{{\n"
                f"\t[{time.strftime('%Y-%m-%d %H:%M:%S')}] \n"
                f" [LOGGING]: \n{text}\n"
                f"}}\n")
        f.close()


def write_file(path: str, text: str) -> bool:
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
            f.close()
        return True
    except:
        return False


def load_rules(configure_default) -> dict:
    """加载规则文件"""
    # 如果没有规则文件就创建
    if not os.path.isfile(f"./intelligence/rules/{configure_default}.json"):
        with open(f"./intelligence/rules/{configure_default}.json", "w", encoding="utf-8") as f:
            json.dump({}, f, indent=3, ensure_ascii=False)
            f.close()

    with open(f"./intelligence/rules/{configure_default}.json", "r", encoding="utf-8") as f:
        rules = json.load(f)
        f.close()
    return rules


def save_rules(rule: dict, configure_default: str):
    try:
        with open(f"./intelligence/rules/{configure_default}.json", "w", encoding="utf-8") as f:
            json.dump(rule, f, indent=3, ensure_ascii=False)
            f.close()
        return True
    except:
        return False


def load_api() -> dict:
    with open("./resources/api.json", "r", encoding="utf-8") as f:
        api = json.load(f)
        f.close()
    return api


def save_api(api: dict) -> bool:
    try:
        with open("./resources/api.json", "w", encoding="utf-8") as f:
            json.dump(api, f, indent=3, ensure_ascii=False)
            f.close()
        return True
    except:
        return False


def add_character(model_path: str) -> bool:
    try:
        shutil.copytree(model_path, f"./resources/model/{model_path.split('/')[-1]}/")
        return True
    except:
        return False


def delete_character(configure: dict, model: str) -> bool:
    if os.path.exists(f"./resources/voice/{model}"):
        shutil.rmtree(f"./resources/voice/{model}")
        del configure['model'][model]
        save_configure(configure)
    if os.path.exists(f"./intelligence/prompts/{model}.json"):
        os.remove(f"./intelligence/prompts/{model}.json")
    if os.path.exists(f"./intelligence/rules/{model}.json"):
        os.remove(f"./intelligence/rules/{model}.json")
    shutil.rmtree(f"./resources/model/{model}")
    return True


def get_configure_actions(configure: dict, configure_default: str,
                          type_: typing.Literal['nor', 'spec'] = 'nor') -> dict:
    """加载动作配置"""
    return configure['model'][configure_default]['action' if type_ == 'nor' else 'special_action']


def get_audio_path(configure: dict, configure_default: str, action: str) -> str:
    """加载音频路径"""
    try:
        return (f"./resources/voice/{configure['default']}/"
                f"{get_configure_actions(configure, configure_default)[action]['play']}/"
                f"{random.choice(configure['model'][configure['default']]['voice'][configure['model'][
                    configure_default]['action'][action]['play']])
                    if get_configure_actions(configure, configure_default)[action]['play_type'] == 'random' else
                    get_configure_actions(configure, configure_default)[action]['play_type']}")
    except (KeyError, IndexError):
        return ""


def load_template_model(configure: dict, model: str) -> None:
    """加载模板模型"""
    with open("./resources/template.json", "r", encoding="utf-8") as tf:
        template = json.load(tf)
        tf.close()
    if not os.path.exists(f"./resources/voice/{model}"):
        os.mkdir(f"./resources/voice/{model}")
        for template_dir in template['voice'].keys():
            try:
                os.mkdir(f"./resources/voice/{model}/{template_dir}")
            except FileExistsError:
                pass
    for emotion_type in os.listdir(f"./resources/voice/{model}"):
        template['voice'][emotion_type] = list(map(lambda v: v.split("\\")[-1], __import__("glob").glob(
            f"./resources/voice/{model}/{emotion_type}/*.wav")))
    configure['model'].update({model: template})
    with open("./resources/configure.json", "w", encoding="utf-8") as sf:
        json.dump(configure, sf, indent=3, ensure_ascii=False)
        sf.close()
    # 规则文件
    if not os.path.isfile(f"./intelligence/rules/{model}.json"):
        with open(f"./intelligence/rules/{model}.json", "w", encoding="utf-8") as f:
            json.dump({}, f, indent=3, ensure_ascii=False)
            f.close()
    # 提示文件
    if not os.path.isfile(f"./intelligence/prompts/{model}.json"):
        with open(f"./intelligence/prompts/{model}.json", "w", encoding="utf-8") as f:
            json.dump({}, f, indent=3, ensure_ascii=False)
            f.close()
    if not os.path.exists(f"./resources/voice/{model}"):
        load_template_model(configure, model)
    if not os.path.exists(f"./intelligence/prompts/{model}.json"):
        load_template_model(configure, model)
    if not os.path.exists(f"./intelligence/rules/{model}.json"):
        load_template_model(configure, model)


def load_language(configure: dict) -> list[str]:
    """加载语言配置"""
    system_language = locale.getlocale()[0]
    # 自动选择语言
    if not configure['settings']['language'].strip():
        configure['settings']['language'] = system_language
    # 配置语言
    if configure['settings']['language'] in os.listdir("./resources/languages"):
        system_language = configure['settings']['language']
    else:
        # 进行相似度比较
        similarities = {}
        for language in os.listdir("./resources/languages"):
            similarity = difflib.SequenceMatcher(None, system_language, language).ratio()
            similarities[language] = similarity
        best_match = max(similarities, key=similarities.get)
        print(f"Language Match Similarities: \n{similarities}\n\nAuto Select: {best_match}")
        configure['settings']['language'] = best_match
        system_language = best_match
    with open(f"./resources/languages/{system_language}", "r", encoding="utf-8") as f:
        languages: list[str] = f.read().split("\n")
        f.close()
    return languages


def load_switch() -> dict:
    """加载开关配置"""
    with open("./interface/setting/sub_general/switch.json", "r", encoding="utf-8") as f:
        switch = json.load(f)
        f.close()
    return switch


def save_switch(switch: dict) -> None:
    """保存开关配置"""
    with open("./interface/setting/sub_general/switch.json", "w", encoding="utf-8") as f:
        json.dump(switch, f, indent=3, ensure_ascii=False)
        f.close()


def load_configure(subscribe) -> tuple[dict, str]:
    """加载配置"""
    with open("./resources/configure.json", "r", encoding="utf-8") as f:
        def recover_backup():
            nonlocal configure
            os.remove("./resources/configure.json")
            shutil.copy2("./logs/backup/configure.json", "./resources/configure.json")
            with open("./resources/configure.json", "r", encoding="utf-8") as lf:
                configure = json.load(lf)
                lf.close()

        # 错误检查器
        try:
            configure = json.load(f)
        except json.JSONDecodeError:
            f.close()
            recover_backup()

        try:
            configure_default = configure["default"]

            configure['model'][configure['default']]['adult'] = configure['model'][configure_default]['adult']
            configure['model'][configure['default']]['voice'] = configure['model'][configure_default]['voice']
        except KeyError:
            f.close()
            recover_backup()
            return load_configure(subscribe)
        f.close()

    # 写入接口
    subscribe.Register.SetCharacter(configure['default'])
    subscribe.Register.SetVoiceModel(configure['voice_model'])
    subscribe.Register.SetName(configure['name'])

    return configure, configure_default


def save_configure(configure: dict) -> None:
    """保存配置"""
    with open("./resources/configure.json", "w", encoding="utf-8") as f:
        json.dump(configure, f, indent=3, ensure_ascii=False)
        f.close()
