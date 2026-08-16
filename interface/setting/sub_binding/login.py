import typing
import hashlib

from ..customize import widgets

from PyQt5.Qt import QRect, QWidget, QThread, pyqtSignal
from qfluentwidgets import LineEdit, PasswordLineEdit, BodyLabel, TextEdit, PrimaryPushButton, \
    FluentIcon, CheckBox


with open("./resources/token/token.aes", "r", encoding="utf-8") as rf:
    token = rf.read()
    rf.close()


class Loading(QThread):
    result = pyqtSignal(dict)

    def __init__(self, parent: QWidget, runtime_module, type_: typing.Literal['login', 'policy', "auto-login"]):
        super().__init__(parent)
        self.runtime = runtime_module
        self.type_ = type_

    def run(self):
        if self.type_ == 'login':
            self.result.emit(self.runtime.user_login(
                self.parent().input_email.text(),
                hashlib.md5(str(self.parent().input_password.text()).encode("utf-8")).hexdigest(),
                self.parent().click_next_auto_login.isChecked(),
            ))
        elif self.type_ == 'auto-login':
            self.result.emit(self.runtime.user_login(
                self.parent().input_email.text(),
                hashlib.md5(str(self.parent().input_password.text()).encode("utf-8")).hexdigest(),
                self.parent().click_next_auto_login.isChecked(),
                token.replace(" ", "")
            ))
        elif self.type_ == 'policy':
            self.result.emit({"message": self.runtime.get_policy()})


class Login(QWidget):
    def __init__(self, languages, configure, runtime_module, addSubInterface):
        super().__init__()
        self.token = token
        self.runtime = runtime_module
        self.languages = languages
        self.configure = configure
        self.addSubInterface = addSubInterface
        self.setObjectName("Login")

        BodyLabel(languages[146], self).setGeometry(QRect(5, 5, 100, 35))
        self.input_email = LineEdit(self)
        self.input_email.setClearButtonEnabled(True)
        self.input_email.setGeometry(QRect(110, 5, 400, 35))

        BodyLabel(languages[147], self).setGeometry(QRect(5, 45, 100, 35))
        self.input_password = PasswordLineEdit(self)
        self.input_password.setClearButtonEnabled(True)
        self.input_password.setGeometry(QRect(110, 45, 400, 35))

        policy = TextEdit(self)
        policy.setReadOnly(True)
        policy_thread = Loading(self, self.runtime, 'policy')
        policy_thread.result.connect(lambda result: policy.setMarkdown(result['message']))
        policy_thread.start()
        policy.setGeometry(QRect(0, 85, 620, 250))

        self.click_next_auto_login = CheckBox(self.languages[152], self)
        self.click_next_auto_login.setGeometry(QRect(0, 345, 620, 35))

        self.click_login = PrimaryPushButton(FluentIcon.SEND, self.languages[148], self)
        self.click_login.setGeometry(QRect(0, 380, 620, 35))
        self.click_login.clicked.connect(self.login)
        if token:
            policy_thread = Loading(self, self.runtime, 'auto-login')
            policy_thread.result.connect(self.wrapper)
            policy_thread.start()

    def wrapper(self, result):
        widgets.pop_info(self, self.languages[148], result['message'])
        if result['token'] and result['status']: self.token = result['token']
        if (not token.strip() or self.click_next_auto_login.isChecked()) and result['status']:
            with open("./resources/token/token.aes", "w", encoding="utf-8") as f:
                f.write(result['token'])
                f.close()

    def login(self):
        policy_thread = Loading(self, self.runtime, 'login')
        policy_thread.result.connect(self.wrapper)
        policy_thread.start()
