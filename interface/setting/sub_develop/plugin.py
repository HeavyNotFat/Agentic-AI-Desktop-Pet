import os

from ..customize import function
from ..customize import widgets

from PyQt5.Qt import QRect
from PyQt5.QtWidgets import QWidget, QButtonGroup

from qfluentwidgets import PrimaryPushButton, BodyLabel, LineEdit, ComboBox, RadioButton, FluentIcon


class PluginBinding(QWidget):
    def __init__(self, interface_module, run_function: callable, languages, configure, **kwargs):
        super().__init__()
        self.run_function = run_function
        self.languages = languages
        self.configure = configure
        self.kwargs = kwargs
        self.setObjectName("PluginBinding")

        BodyLabel(self.languages[75], self).setGeometry(QRect(20, 52, 200, 30))
        self.input_plugin_folder = LineEdit(self)
        self.input_plugin_folder.setGeometry(QRect(120, 52, 400, 30))

        self.click_select_folder = PrimaryPushButton(self.languages[134], self)
        self.click_select_folder.setGeometry(QRect(530, 52, 100, 35))
        self.click_select_folder.clicked.connect(self.fill_plugin_information)


        self.input_codes = widgets.CodeEdit(interface_module, self)
        self.input_codes.setText(open("./interface/subscribe/examples/example_getattr",
                                      "r", encoding="utf-8").read())
        self.input_codes.setPlaceholderText("Emm. The developer is slacking off again")
        self.input_codes.setGeometry(QRect(10, 102, 620, 320))

        self.select_examples = ComboBox(self)
        examples = os.listdir("./interface/subscribe/examples")
        self.select_examples.addItems(examples)
        self.select_examples.setGeometry(QRect(590, 102, 40, 30))
        self.select_examples.setCurrentText("example_getattr")
        self.select_examples.currentTextChanged.connect(
            lambda: self.input_codes.setText(
                open(f"./interface/subscribe/examples/{examples[self.select_examples.currentIndex()]}",
                     "r", encoding="utf-8").read()))

        self.click_running = PrimaryPushButton(self.languages[110], self)
        self.click_running.setIcon(FluentIcon.CARE_RIGHT_SOLID)
        self.click_running.setGeometry(QRect(10, 432, 100, 30))
        self.click_running.clicked.connect(self.run)

        self.button_groups = QButtonGroup(self)
        self.single_enhancement = RadioButton(self.languages[112], self)
        self.single_independent = RadioButton(self.languages[113], self)
        self.single_automatic = RadioButton(self.languages[114], self)
        self.single_automatic.setChecked(True)
        self.single_enhancement.setGeometry(QRect(130, 432, 150, 30))
        self.single_independent.setGeometry(QRect(280, 432, 150, 30))
        self.single_automatic.setGeometry(QRect(430, 432, 150, 30))
        self.button_groups.addButton(self.single_enhancement)
        self.button_groups.addButton(self.single_independent)
        self.button_groups.addButton(self.single_automatic)

        self.click_compile = PrimaryPushButton(self.languages[193], self)
        self.click_compile.clicked.connect(self.compile)
        self.click_compile.setGeometry(QRect(10, 472, 620, 30))

    def compile(self):
        self.kwargs.get('compile_plugin')(self.button_groups.checkedId(), self.input_plugin_folder.text())

    def fill_plugin_information(self):
        folder_path = function.select_folder(self, self.languages[40], self.input_plugin_folder)
        general_entrance = f"{folder_path}/main.py"
        if os.path.isfile(general_entrance):
            self.input_codes.clear()
            self.input_codes.setPlainText(open(general_entrance, "r", encoding="utf-8").read())
        else:
            self.input_plugin_folder.clear()
            widgets.pop_error(self, self.languages[112], self.languages[118])

    def run(self):
        self.run_function(self.input_codes.toPlainText(), self.button_groups.checkedId())
