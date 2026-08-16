from . import Config as _Config
from . import Register as _Register

from . import operate


class _Operate(operate.Operate):
    def __init__(self):
        super().__init__(Config)


class __Register(_Register.Register):
    def __init__(self):
        super().__init__(Config)


Config = _Config.Config()
Register = __Register()
Operate = _Operate()
