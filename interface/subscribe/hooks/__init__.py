from . import Register as _register
from . import Config as _Config
from . import operate


class _Register(_register.Register):
    def __init__(self):
        super().__init__(Config)


class _Operate(operate.Operate):
    def __init__(self):
        super().__init__(Config)


Config = _Config.Config()
Register = _Register()
Operate = _Operate()
