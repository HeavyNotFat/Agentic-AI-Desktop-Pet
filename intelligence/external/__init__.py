import ctypes
from urllib.parse import unquote, urlparse
import pathlib
import json
import time

import requests
import dashscope


def draw_picture_by_qwen(prompts):
    """画画工具"""
    rsp = dashscope.ImageSynthesis.call(model='wanx2.1-t2i-turbo', prompt=prompts, n=1, size='1024*1024')
    filepath = 'ERROR'
    for result in rsp.output.results:
        file_name = pathlib.PurePosixPath(unquote(urlparse(result.url).path)).parts[-1]
        filepath = f'./logs/picture/{file_name}'
        with open(filepath, 'wb+') as f:
            f.write(requests.get(result.url).content)
            time.sleep(0.05)
            f.close()

    return json.dumps({'filepath': filepath})

def picture_understand(description, image_path):
    conversation = {'role': 'user', 'content': [{'static': f'file://{image_path}'}, {'text': description}]}
    completion = dashscope.MultiModalConversation().call(api_key=dashscope.api_key, model='qwen-vl-max', messages=[conversation])
    msg = completion['output']['choices'][0]['message'].content[0]['text']
    return msg

def get_current_time():
    """
    当你想获取时间时非常有用
    """
    return f'当前时间：{time.strftime('%Y-%m-%d %H:%M:%S')}'

def find_file(filename):
    drives = []
    exits_path = []
    bitmask = ctypes.cdll.kernel32.GetLogicalDrives()
    for letter in range(65, 91):
        if bitmask & 1:
            drives.append(chr(letter) + ':\\')
        bitmask >>= 1
    if len(drives) > 1:
        for drive in drives:
            if drive == 'C:\\':
                continue
            else:
                for file_path in pathlib.Path(drive).rglob(filename):
                    exits_path.append(str(file_path))
        return json.dumps({'status': 'success', 'result': exits_path})
    else:
        return json.dumps({'status': 'failure', 'result': '无权限访问'})

def load_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"failure: {e}"

def save_file(filepath, content):
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
            f.close()
            return "success"
    except Exception as e:
        return f"failure: {e}"
