import random

from .. import standards

from PyQt5.QtWidgets import QWidget
from qfluentwidgets import FluentIcon


class Setting:
    def __init__(self, config):
        self.config = config

    def InsertInterface(self, widget: QWidget, icon: FluentIcon, text: str, parent=None):
        """
        插入一个界面接口进入设置
        :param widget: QWidget -->  PyQt5.QtWidgets
        :param icon: FluentIcon  -->  qfluentwidgets
        :param text: String   -->   文本显示
        :param parent: QWidget | standards-->  PyQt5.QtWidgets
        """
        if not widget.objectName():
            widget.setObjectName(f"_Default{text.title()}{str(random.randint(0, 999999)).zfill(6)}")
        elif widget.objectName() == "79JWnYp65lhmjxPa1zTru+NR43o86dPk3Lj821+Tlld0DRaZIHMRAs+uOYavQi1t":
            return

        # 复制新的父类
        if parent == standards.SUB_PROGRAM_SELF:
            copy_parent = self.config['program_self']
        elif parent == standards.SUB_GENERAL:
            copy_parent = self.config['general']
        elif parent == standards.SUB_INTELLIGENCE:
            copy_parent = self.config['intelligence']
        elif parent == standards.SUB_BINDING:
            copy_parent = self.config['binding']
        elif parent == standards.SUB_DEVELOPER:
            copy_parent = self.config['dev']
        elif parent == standards.SUB_ABOUT:
            copy_parent = self.config['about']
        else:
            copy_parent = parent

        self.config['setting'].addSubInterface(widget, icon, text, parent=copy_parent)

    def DeleteInterface(self, widget: QWidget):
        """
        删除一个界面接口
        :param widget: QWidget -->  PyQt5.QtWidgets
        """
        self.config['setting'].navigation_interface.removeWidget(widget.objectName())
