import re

from .. import customize

from PyQt5.QtWidgets import QWidget
from PyQt5.Qt import QRect, QFileDialog
from qfluentwidgets import BodyLabel, LineEdit, PrimaryToolButton, FluentIcon, CheckBox, ComboBox


class ToolsBinding(QWidget):
    def __init__(self, languages, configure, runtime_module, interface_module):
        super().__init__()
        self.languages = languages
        self.configure = configure
        self.runtime_module = runtime_module
        self.setObjectName("ToolsBinding")

        self.required_check_button_value: dict[str, CheckBox] = {}

        # 准备
        BodyLabel(self.languages[37], self).setGeometry(QRect(0, 42, 150, 30))
        self.python_file_path = LineEdit(self)
        self.python_file_path.setClearButtonEnabled(True)
        self.python_file_path.setGeometry(QRect(160, 42, 430, 30))
        self.python_file_path.textChanged.connect(self.fill_python_file)

        self.click_select_file = PrimaryToolButton(self)
        self.click_select_file.clicked.connect(self.select_file)
        self.click_select_file.setIcon(FluentIcon.FOLDER_ADD)
        self.click_select_file.setGeometry(QRect(600, 42, 30, 30))

        self.python_code_editor = customize.widgets.CodeEdit(interface_module, self)
        self.python_code_editor.setGeometry(QRect(0, 80, 640, 100))

        # 选择
        BodyLabel(self.languages[79], self).setGeometry(QRect(0, 190, 100, 30))
        self.select_entrance = ComboBox(self)
        self.select_entrance.setGeometry(QRect(110, 190, 200, 30))
        self.input_entrance_description = LineEdit(self)
        self.input_entrance_description.setPlaceholderText(self.languages[244])
        self.input_entrance_description.setGeometry(QRect(320, 190, 320, 30))

    def select_file(self):
        self.python_file_path.setText(QFileDialog.getOpenFileName(
            self, "Python File", "", "Python File (*.py)"
        )[0])

    def fill_python_file(self, a0):
        with open(a0, "r", encoding="utf-8") as f:
            tool_code = f.read()
            f.close()
        self.python_code_editor.setPlainText(tool_code)
        type_mapping = {
            'str': self.languages[240],
            'int': self.languages[241],
            'list': self.languages[242],
            'bool': self.languages[243],
            'float': self.languages[241],
            'unknown': 'unknown'
        }

        matches = re.findall(r'def\s+(\w+)\s*\(([^)]*)\)', tool_code)

        function_names = []
        x, y = 20, 300

        self.required_check_button_value = {}
        for match in matches:
            function_name = match[0]
            function_names.append(function_name)
            parameters = match[1].split(',')
            parameters = [param.strip() for param in parameters]

            for param in parameters:
                if '=' in param:
                    required_value = False
                    key, value = param.split('=')
                    key = key.strip()
                    value = value.strip()
                    if ':' in key:
                        param_name, param_type = key.split(':')
                        param_name = param_name.strip()
                    else:
                        param_name = key

                    if value.startswith('"') and value.endswith('"'):
                        param_type = 'string'
                    elif value.isdigit():
                        param_type = 'integer'
                    elif re.match(r'^-?\d+\.\d+$', value):
                        param_type = 'float'
                    elif value.lower() in ['true', 'false']:
                        param_type = 'boolean'
                    else:
                        param_type = 'unknown'

                else:
                    required_value = True
                    if ':' in param:
                        param_name, param_type = param.split(':')
                        param_name = param_name.strip()
                        param_type = param_type.strip()
                    else:
                        param_name = param
                        param_type = 'unknown'
                    param_type = type_mapping.get(param_type, param_type)
                try:
                    selected_function = function_names[function_names.index(self.select_entrance.text())]
                except ValueError:
                    selected_function = function_names[0]
                if (not param_name or
                        selected_function != function_name):
                    continue

                check = CheckBox(self)
                check.setText(param_name)
                check.setChecked(required_value)

                type_combo = ComboBox(self)
                type_combo.addItems(list(type_mapping.values()))
                if param_type != "unknown":
                    type_combo.setCurrentText(param_type)

                value_description = LineEdit(self)
                value_description.setText(self.languages[244])
                self.required_check_button_value.update(
                    {param_name: {'check': check,
                                  'value': required_value,
                                  'description': value_description,
                                  'type': type_combo}})

                type_combo.setGeometry(QRect(x + 120, y, 120, 30))
                value_description.setGeometry(QRect(x + 120 + 70, y, 120, 30))
                check.setGeometry(QRect(x, y, 120, 30))
                x += 270
                if x > 400:
                    x = 20
                    y += 30

        self.select_entrance.clear()
        self.select_entrance.addItems(function_names)

        function_doc_string = self.languages[244]
        extraction_doc = self.runtime_module.ExtractFunctionDocstring(
            self.select_entrance.text()
        ).extract(tool_code)
        if extraction_doc is not None:
            function_doc_string = extraction_doc
        self.input_entrance_description.setText(function_doc_string)

