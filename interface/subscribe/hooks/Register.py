from PyQt5.QtWidgets import QWidget


class Register:
    def __init__(self, config):
        self.config = config

    def HookSettingInterface(self, new_widget: QWidget):
        """
        阶段原设置界面接口，右键打开设置会重定向变成新的接口
        :param new_widget: QWidget -->  PyQt5.QtWidgets
        """
        self.config.register("setting", new_widget)

    def HookConversationInterface(self, new_widget: QWidget):
        """
        阶段原对话界面接口，右键打开对话会重定向变成新的接口
        :param new_widget: QWidget -->  PyQt5.QtWidgets
        """
        self.config.register("conversation", new_widget)

    def AddHookCloseProgram(self, func: callable):
        self.config.register("close_program", func)
