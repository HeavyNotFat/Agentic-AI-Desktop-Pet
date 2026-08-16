# 为外部导入做好准备
from . import thread
from . import file
from . import reg

import os
import base64
import tempfile
import ast
import threading
import time
import re
import struct
from pathlib import Path

import mss
import numpy
import requests
import win32api
import win32con
import win32com.client


class PassedNoneContent(object):
    pass


api_source = None
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0"
HEADERS = {
    "User-Agent": USER_AGENT,
}
SENSITIVE_CONTENT = [
    "/resources/configure.json",
    PassedNoneContent(),  # 占位符
    PassedNoneContent(),  # 占位符
]
major = "3"
minor = "16"
patch = "3"


class ExtractFunctionDocstring(ast.NodeVisitor):
    """提取函数文档字符串 Extract function docstring"""
    def __init__(self, function_name):
        self.function_name = function_name
        self.description = None

    def visit_FunctionDef(self, node):
        if isinstance(node.parent, ast.Module) and node.name == self.function_name:
            docstring = ast.get_docstring(node)
            if docstring:
                lines = docstring.split('\n')
                if lines:
                    self.description = lines[0].strip()
        return node

    @staticmethod
    def add_parents(tree):
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node

    def extract(self, code):
        tree = ast.parse(code)
        self.add_parents(tree)
        visitor = ExtractFunctionDocstring(self.function_name)
        visitor.visit(tree)

        return visitor.description


class RemoveFunctionTransformer(ast.NodeTransformer):
    """移除函数 Remove function"""
    def __init__(self, function_name):
        self.function_name = function_name

    def visit_FunctionDef(self, node):
        if isinstance(node.parent, ast.Module) and node.name == self.function_name:
            return None
        return node

    @staticmethod
    def add_parents(tree):
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node

    def remove(self, code):
        tree = ast.parse(code)
        self.add_parents(tree)
        transformer = RemoveFunctionTransformer(self.function_name)
        new_tree = transformer.visit(tree)

        return ast.unparse(new_tree)


# 鼠标监听器 Mouse listener
class MouseListener:
    """用于在全局鼠标穿透下进行监听 Used for global mouse penetration to listen"""
    def __init__(self):
        self.listener_thread = None
        self.isListening = False
        self.is_left_button_pressed = False
        self.is_right_button_pressed = False

    def start_listening(self):
        self.isListening = True
        self.listener_thread = threading.Thread(target=self.listen)
        self.listener_thread.start()

    def stop_listening(self):
        self.__init__()

    def listen(self):
        # 初始化鼠标左键和右键的状态变量
        state_left = 0
        state_right = 0

        # 当isListening标志为真时，持续监听鼠标按钮的状态
        while self.isListening:
            # 获取当前鼠标左键和右键的状态
            current_state_left = win32api.GetKeyState(win32con.VK_LBUTTON)
            current_state_right = win32api.GetKeyState(win32con.VK_RBUTTON)

            # 检查鼠标左键状态是否有变化
            if current_state_left != state_left:
                state_left = current_state_left
                # 当鼠标左键被按下时，设置相应标志为真
                if current_state_left < 0:
                    self.is_left_button_pressed = True
                # 当鼠标左键被释放时，设置相应标志为假
                else:
                    self.is_left_button_pressed = False

            # 检查鼠标右键状态是否有变化
            if current_state_right != state_right:
                state_right = current_state_right
                # 当鼠标右键被按下时，设置相应标志为真
                if current_state_right < 0:
                    self.is_right_button_pressed = True
                # 当鼠标右键被释放时，设置相应标志为假
                else:
                    self.is_right_button_pressed = False

            # 线程暂停0.01秒，以减少CPU占用
            threading.Event().wait(0.01)


class PythonCodeParser(ast.NodeVisitor):
    """Parse plugin code"""
    def __init__(self, code):
        super().__init__()
        self.called = [False] * 10
        self.analyze_code(code)

    @property
    def has_subscribe(self):
        return self.called[0]

    @property
    def has_subscribe_for_views(self):
        return self.called[1]

    @property
    def has_subscribe_for_actions(self):
        return self.called[2]

    def analyze_code(self, code):
        tree = ast.parse(code)
        self.visit(tree)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            current_node = node.func
            parts = []
            while isinstance(current_node, ast.Attribute):
                parts.append(current_node.attr)
                current_node = current_node.value
            if isinstance(current_node, ast.Name):
                parts.append(current_node.id)
                full_call_path = '.'.join(reversed(parts)).split(".")
                if full_call_path[0] == "interface":
                    self.called[0] = True
                if full_call_path[0] == "interface" and full_call_path[2] == "views":
                    self.called[1] = True
                if full_call_path[0] == "interface" and full_call_path[2] == "actions":
                    self.called[2] = True
        self.generic_visit(node)


class PythonCodeExaminer(ast.NodeVisitor):
    """
    内容审计 用于检查插件代码安全（用户可以自行开启）
    开启：死循环检测 (无法关闭)
    分为5个等级:
     L1: 轻微保护（
                    仅审计读取./resources/configure.json
                用户自行判断是否运行）
     L2: 轻度保护（
                    仅审计读取./resources/configure.json文件。
                    有支持有云访问能力的插件。
                用户自行判断是否运行）
     L3: 中度保护（
                    审计以上内容
                    是否调用(
                        exec, eval
                    )，
                程序先阻止运行用户可以手动运行）
     L4: 高度保护（
                    审计所有内容
                    库导入内容(
                        os, sys
                    )
                程序直接阻止，无法运行）
     L5: 重度保护（
                    审计所有内容
                    库导入内容(
                        pickle, subprocess, shutil,
                        importlib, ctypes, cffi
                    )，
                程序直接阻止，无法运行）
    """
    def __init__(self, code):
        self.code = code
        self.exists = [False] * 10
        self.code_optimise = [False] * 10
        self.imported_modules = set()
        self.analyze()

    def analyze(self):
        tree = ast.parse(self.code)
        self.visit(tree)

    # 判断
    @property
    def is_l1(self):
        return self.is_quoted_config

    @property
    def is_l2(self):
        return self.is_l1 or self.is_imported_requests or self.is_imported_websocket

    @property
    def is_l3(self):
        return self.is_l2 or self.is_called_execute_or_evaluate

    @property
    def is_l4(self):
        return self.is_l3 or self.is_imported_os_or_sys

    @property
    def is_l5(self):
        return self.is_l4 or \
                self.is_imported_ctypes_or_cffi or self.is_imported_pickle or self.is_imported_subprocess or \
                self.is_imported_shutil, self.is_imported_importlib

    # 代码优化建议
    @property
    def optimize_infinite_loop(self):
        return self.code_optimise[0]

    # 子
    @property
    def is_quoted_config(self):
        return self.exists[0]

    @property
    def is_called_execute_or_evaluate(self):
        return self.exists[1]

    @property
    def is_called_compile(self):
        return self.exists[2]

    @property
    def is_imported_websocket(self):
        return "websocket" in self.imported_modules

    @property
    def is_imported_requests(self):
        return "requests" in self.imported_modules

    @property
    def is_imported_os_or_sys(self):
        return "os" in self.imported_modules or "sys" in self.imported_modules

    @property
    def is_imported_ctypes_or_cffi(self):
        return "ctypes" in self.imported_modules or "cffi" in self.imported_modules

    @property
    def is_imported_pickle(self):
        return "pickle" in self.imported_modules

    @property
    def is_imported_subprocess(self):
        return "subprocess" in self.imported_modules

    @property
    def is_imported_shutil(self):
        return "shutil" in self.imported_modules

    @property
    def is_imported_importlib(self):
        return "importlib" in self.imported_modules

    def custom_examine_library(self, module):
        return module in self.imported_modules

    def visit_Call(self, node):
        """审计函数调用"""
        if isinstance(node.func, ast.Name):
            if node.func.id == 'exec':
                self.exists[1] = True
            elif node.func.id == 'eval':
                self.exists[1] = True
            elif node.func.id == 'compile':
                self.exists[2] = True
        self.generic_visit(node)

    def visit_Str(self, node):
        """审计字符串"""
        for index, content in enumerate(SENSITIVE_CONTENT):
            if content in node.s:
                self.exists[index] = True
        self.generic_visit(node)

    def visit_Constant(self, node):
        """审计字符串"""
        if isinstance(node.value, str):
            for index, content in enumerate(SENSITIVE_CONTENT):
                if isinstance(content, PassedNoneContent):
                    continue
                if content in node.value:
                    self.exists[index] = True
        self.generic_visit(node)

    def visit_Import(self, node):
        """审计 以import导入的库"""
        for alias in node.names:
            self.imported_modules.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """审计 以from导入的库"""
        if node.module:
            self.imported_modules.add(node.module)
        self.generic_visit(node)

    def visit_While(self, node):
        """审计 while关键字是否存在死循环"""
        is_condition = False
        if isinstance(node.test, ast.Constant) and node.test.value in (True, 1):
            is_condition = True
        elif isinstance(node.test, ast.NameConstant) and node.test.value is True:
            is_condition = True
        if is_condition:
            has_break = any(isinstance(n, ast.Break) for n in ast.walk(node))
            if not has_break:
                self.code_optimise[0] = True
        self.generic_visit(node)


def parse_local_url(url: str):
    truly_url = url.format(
        ip=__import__("socket").gethostbyname(__import__("socket").gethostname()),
        year=time.strftime("%Y"),
    )
    cleaned_url = re.sub(r'\s*\+\s*', '+', truly_url)
    pattern = r'^(http|https|ws)://([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)(:(.*?))?(/.*)?$'
    match = re.match(pattern, cleaned_url)
    if match:
        request_header = match.group(1)
        ip = match.group(2)
        port_part = match.group(4) if match.group(4) else '80'
        path = match.group(5) if match.group(5) else '/'
        try:
            port = str(eval(port_part)) if port_part else '80'
        except Exception:
            return url

        return f"{request_header}://{ip}:{port}{path}"
    return url


def capture() -> str:
    try:
        os.remove(f"{tempfile.gettempdir()}/screenshot.png")
    except FileNotFoundError:
        pass
    with mss.mss() as sct:
        sct.shot(output=f"{tempfile.gettempdir()}/screenshot.png")
    return f"{tempfile.gettempdir()}/screenshot.png".replace("\\", "/")


def check_update() -> bool | None:
    try:
        latest_version = requests.post(f"{api_source}/update/version.php",
                                       headers=HEADERS).json()['version']
    except:
        return None
    if latest_version == f"{major}.{minor}.{patch}":
        return True
    else:
        return latest_version


def get_notice_board() -> str:
    request = ""
    try:
        request = '\n'.join(requests.get(f"{api_source}/notice/get.php",
                                         headers=HEADERS).json(),)
    except:
        pass
    return request


def get_policy() -> str:
    request = ""
    try:
        request = '\n'.join(requests.get(f"{api_source}/notice/get_policy.php",
                                         headers=HEADERS).json())
    except:
        pass
    return request


def user_register(email) -> dict:
    try:
        register_response = requests.post(f"{api_source}/account/register.php", json={'to': email},
                                          headers=HEADERS)
        if register_response.json().get('error'):
            return {"status": False, "message": register_response.json()['error']}
        else:
            return {"status": True, "message": register_response.json()['success']}
    except:
        return {"status": False, "message": "发送邮件错误！"}


def user_verify(email, code, password) -> dict:
    try:
        verify_response = requests.post(f"{api_source}/account/verify.php",
                                         json={'email': email, 'code': code, 'password': password},
                                         headers=HEADERS)
        if verify_response.json().get('error'):
            return {"status": False, "message": verify_response.json()['error']}
        else:
            return {"status": True, "message": verify_response.json()['success']}
    except:
        return {"status": False, "message": "验证错误！"}


def user_login(email, password, auto_login: bool = False, session: str = "") -> dict:
    try:
        login_response = requests.post(f"{api_source}/account/login.php",
                                       json={'email': email, 'password': password,
                                             "auto_login": auto_login, "session": session},
                                       headers=HEADERS)
        if login_response.json().get('error'):
            return {"status": False, "token": None,
                    "message": login_response.json()['error']}
        else:
            t = ""
            if auto_login:
                t = login_response.json()['session']
            return {"status": True, "token": t, "role": login_response.json()['role'],
                    "message": login_response.json()['success']}
    except Exception as e:
        return {"status": False, "message": "登录错误！"}


def get_shop_model() -> dict:
    try:
        model_lists = requests.get(f"{api_source}/model/get_model.php").json()
        return {"name": list(map(lambda v: ".".join(v.split(".")[:-1]), model_lists['archives'])),
                "list": model_lists['archives'],
                "url": model_lists['urls'],
                "static": model_lists['icons'],
                "description": model_lists['descriptions'],
                }
    except:
        return {
            "name": [],
            "list": [],
            "url": [],
            "static": [],
            "description": [],
        }


def get_plugin() -> dict:
    try:
        model_lists = requests.get(f"{api_source}/plugin/get_plugin.php").json()
        return {"name": list(map(lambda v: ".".join(v.split(".")[:-1]), model_lists['archives'])),
                "list": model_lists['archives'],
                "url": model_lists['urls'],
                "static": model_lists['icons'],
                "config": model_lists['config'],
                "description": model_lists['descriptions'],
                }
    except:
        return {
            "name": [],
            "list": [],
            "url": [],
            "static": [],
            "config": [],
            "description": [],
        }


def upload_file(filepath: list, type_: str, token: str) -> tuple[bool, str]:
    filename = []
    file_base64 = []
    for image_path in filepath:
        with open(image_path, "rb") as image_file:
            filename.append(os.path.basename(image_path))
            file_base64.append(base64.b64encode(image_file.read()).decode('utf-8'))
            image_file.close()
    try:
        r = requests.post(f"{api_source}/community/upload.php",
                          json={"type": type_, "token": token, "filename": filename, "fileb64": file_base64})
        return r.json()['status'], r.json()['msg']
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def find_internal_recording_device(p) -> int:
    """寻找内录设备"""
    target = '立体声混音'
    for i in range(p.get_device_count()):
        dev_info = p.get_device_info_by_index(i)
        if dev_info['name'].find(target) >= 0 and dev_info['hostApi'] == 0:
            return i
    return -1


def get_disk_storage_info() -> dict[str, list[int]]:
    """
    获取磁盘信息 (MB)
    :return
    {
        "<DiskID Symbol>": [<Current ID Total Size>, <Current ID Free Size>],
        "*": [<Disk Total Size>, <Disk Free Size>]
    }
    """
    total_space = 0
    free_space = 0
    storage_data = {}

    c = win32com.client.GetObject('winmgmts:')
    disks = c.ExecQuery("Select * from Win32_LogicalDisk Where DriveType=3")
    for disk in disks:
        storage_data.update({str(disk.DeviceID): [int(disk.Size) // (1024 ** 2), int(disk.FreeSpace) // (1024 ** 2)]})
        total_space += int(disk.Size)
        free_space += int(disk.FreeSpace)
    storage_data.update({"*": [total_space // (1024 ** 2), free_space // (1024 ** 2)]})
    return storage_data


def get_program_used_storage() -> int:
    """获取程序已使用的存储 (MB)"""
    total_size = 0
    folder_path = Path(os.getcwd())

    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = folder_path / dirpath / filename
            try:
                total_size += file_path.stat().st_size
            except (OSError, FileNotFoundError):
                continue

    total_size_gb = round(total_size / (1024 ** 2), 2)
    return total_size_gb

def calculate_rms(data: bytes) -> float:
    """计算RMS音量标准"""
    length = len(data) / 2
    shorts = struct.unpack("%dh" % length, data)
    sum_squares = 0.0
    for sample in shorts:
        n = sample * (1.0 / 32768)
        sum_squares += n * n
    rms = numpy.sqrt(sum_squares / length)
    return rms * 1000


if __name__ == '__main__':
    print(get_plugin())
