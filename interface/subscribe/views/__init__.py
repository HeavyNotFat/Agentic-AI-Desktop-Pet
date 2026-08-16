from .Config import _Config
from . import Register
from . import operate
from . import setting
from . import menu
from . import control


class _ContentMenu(menu.ContentMenu):
    def __init__(self):
        super().__init__(_Config)


class _Operate(operate.Operate):
    def __init__(self):
        super().__init__(_Config)


class _Setting(setting.Setting):
    def __init__(self):
        super().__init__(_Config)


class _Control(control.Control):
    def __init__(self):
        super().__init__(_Config)


class _Register(Register.Register):
    def __init__(self):
        super().__init__(_Config)


_Config = _Config()
Setting = _Setting()
ContentMenu = _ContentMenu()
Operate = _Operate()
Control = _Control()
Register = _Register()
