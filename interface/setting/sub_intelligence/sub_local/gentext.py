from ...customize import function, constants

from PyQt5.Qt import QRect
from PyQt5.QtWidgets import QWidget
from qfluentwidgets import BodyLabel, LineEdit, PasswordLineEdit


INDEX_TOOLTIP = """以'.'分割，程序会依次以键访问数据。
Endpoint实例1： message.content
自定义URL返回： {"status": True, "message": {"role": "assistant", "content": "你好👋，有什么可以帮助你的吗？"}}
程序根据Endpoint切割结果：你好👋，有什么可以帮助你的吗？

Endpoint实例2： fuck.you
自定义URL返回： {"creampie": False, "fuck": {"who": "user", "you": "恶俗！🤢"}}
程序根据Endpoint切割结果：恶俗！🤢
"""


class TextGenerator(QWidget):
    def __init__(self, api_config, parent=None):
        super().__init__(parent)
        self.api_config = api_config
        self.setObjectName("TextGenerator")

        BodyLabel("API-Key", self).setGeometry(QRect(10, 0, 100, 30))
        self.input_api_key_endpoint = LineEdit(self)
        self.input_api_key_endpoint.setPlaceholderText("endpoint")
        self.input_api_key_endpoint.setText(api_config['text']['api'])
        self.input_api_key_endpoint.textChanged.connect(
            lambda value: function.change_configure(value, "text.api",
                                                    self.api_config, constants.API_CONFIGURE_PATH))
        self.input_api_key_endpoint.setGeometry(QRect(100, 0, 100, 30))

        self.input_api_key = PasswordLineEdit(self)
        self.input_api_key.setPlaceholderText("value")
        self.input_api_key.setText(api_config['text']['api-key'])
        self.input_api_key.textChanged.connect(
            lambda value: function.change_configure(value, "text.api-key",
                                                    self.api_config, constants.API_CONFIGURE_PATH))
        self.input_api_key.setGeometry(QRect(200, 0, 200, 30))

        BodyLabel("Messages", self).setGeometry(QRect(10, 40, 300, 30))
        self.input_messages_endpoint = LineEdit(self)
        self.input_messages_endpoint.setPlaceholderText("endpoint")
        self.input_messages_endpoint.setText(api_config['text']['messages'])
        self.input_messages_endpoint.textChanged.connect(
            lambda value: function.change_configure(value, "text.messages",
                                                    self.api_config, constants.API_CONFIGURE_PATH))
        self.input_messages_endpoint.setGeometry(QRect(100, 40, 300, 30))

        BodyLabel("Model", self).setGeometry(QRect(10, 80, 100, 30))
        self.input_model_endpoint = LineEdit(self)
        self.input_model_endpoint.setPlaceholderText("endpoint")
        self.input_model_endpoint.setText(api_config['text']['model'])
        self.input_model_endpoint.textChanged.connect(
            lambda value: function.change_configure(value, "text.model",
                                                    self.api_config, constants.API_CONFIGURE_PATH))
        self.input_model_endpoint.setGeometry(QRect(100, 80, 100, 30))

        self.input_model = LineEdit(self)
        self.input_model.setPlaceholderText("value")
        self.input_model.setText(api_config['text']['model-name'])
        self.input_model.textChanged.connect(
            lambda value: function.change_configure(value, "text.model-name",
                                                    self.api_config, constants.API_CONFIGURE_PATH))
        self.input_model.setGeometry(QRect(200, 80, 200, 30))

        BodyLabel("Tools", self).setGeometry(QRect(10, 120, 300, 30))
        self.input_tools_endpoint = LineEdit(self)
        self.input_tools_endpoint.setPlaceholderText("endpoint")
        self.input_tools_endpoint.setText(api_config['text']['tools'])
        self.input_tools_endpoint.textChanged.connect(
            lambda value: function.change_configure(value, "text.tools",
                                                    self.api_config, constants.API_CONFIGURE_PATH))
        self.input_tools_endpoint.setGeometry(QRect(100, 120, 300, 30))

        index_label = BodyLabel("Answer Index", self)
        index_label.setToolTip(INDEX_TOOLTIP)
        index_label.setGeometry(QRect(10, 160, 100, 30))
        self.input_answer_index = LineEdit(self)
        self.input_answer_index.setPlaceholderText("value")
        self.input_answer_index.setText(api_config['text']['endpoint'])
        self.input_answer_index.textChanged.connect(
            lambda value: function.change_configure(value, "text.endpoint",
                                                    self.api_config, constants.API_CONFIGURE_PATH))
        self.input_answer_index.setGeometry(QRect(100, 160, 300, 30))
