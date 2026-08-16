# 此行用于接口调用！
from . import views
from . import actions
from . import standards
from . import hooks
from . import interact

from .Config import _Config
from . import Register as _Register
from . import character as _character
from . import window as _window
from . import live2d as _live2d
from . import model as _model


class _Character(_character.Character):
    def __init__(self):
        super().__init__(_Config)


class _Window(_window.Window):
    def __init__(self):
        super().__init__(_Config)


class _Live2D(_live2d.Live2D):
    def __init__(self):
        super().__init__(_Config)


class _Model(_model.Model):
    def __init__(self):
        super().__init__(_Config)


class __Register(_Register.Register):
    def __init__(self):
        super().__init__(_Config)


class _RegisterAttribute(_Register.AttributeRegister):
    def __init__(self):
        super().__init__(_Config)


_Config = _Config()
Character = _Character()
Window = _Window()
Live2D = _Live2D()
Model = _Model()
Register = __Register()
RegisterAttribute = _RegisterAttribute()
