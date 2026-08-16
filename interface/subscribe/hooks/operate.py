from PyQt5.QtWidgets import QWidget


class Operate:
    def __init__(self, config):
        self.config = config

    def GetSettingInterface(self) -> QWidget:
        return self.config['setting']

    def GetConversationInterface(self) -> QWidget:
        return self.config['conversation']

    def GetHookCloseProgram(self) -> list[callable]:
        try:
            attr_list = self.config['close_program']
        except (SystemError, AttributeError, IndexError, EOFError, KeyError):
            attr_list = []
        return attr_list
