from . import text
import typing

import requests
import re


def machine_translate(words, target: typing.Literal['zh-Hans', 'en', 'ja', 'ko'] = "ja"):
    # 定义目标URL以获取翻译服务的访问地址
    uri = 'https://cn.bing.com/translator'
    # 发起GET请求获取网页内容，用于提取必要的请求参数
    gi = requests.get(uri).text
    ig = re.search(r'IG:"(.*?)"', gi).group(1)
    token = re.search(r'params_AbusePreventionHelper = (.*?);', gi).group(1)
    tokens = token.replace("[", "")
    js = tokens.split(',')
    t = js[1][1:33]
    url = 'https://cn.bing.com/ttranslatev3?isVertical=1&&IG={}&IID=translator.5027'.format(ig)

    # 准备POST请求的数据，包括源语言、目标语言、文本内容等
    data = {
        'fromLang': 'auto-detect',
        'text': words,
        'to': target,
        'token': t,
        'key': js[0],
        'tryFetchingGenderDebiasedTranslations': 'true'
    }

    # 设置请求的头部信息，模拟浏览器访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    }

    # 发送POST请求，获取翻译服务的响应
    response = requests.post(url, data=data, headers=headers)
    response.raise_for_status()
    translations = response.json()[0]['translations']
    translated_text = translations[0]['text']

    return translated_text


def tongyi_translate(words, target: typing.Literal['Chinese', 'English', 'Japanese', 'Korean'] = "Japanese"):
    CustomGenerate = text.CustomGenerator([{'role': 'user', 'content': words}], True, target)
    return CustomGenerate.generate_text()


if __name__ == '__main__':
    word = input("请输入要翻译的文本：")
    print(machine_translate(word, "zh-Hans"))
