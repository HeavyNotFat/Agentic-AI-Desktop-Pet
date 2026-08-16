import typing
import hashlib

from ..customize import widgets

from PyQt5.Qt import QRect, QWidget, QThread, pyqtSignal, QTimer
from qfluentwidgets import BodyLabel, LineEdit, PasswordLineEdit, PrimaryPushButton, \
    FluentIcon, TextEdit


class Loading(QThread):
    result = pyqtSignal(dict)

    def __init__(self, parent: QWidget,
                 runtime_module, type_: typing.Literal['sms', 'policy', 'verify']):
        self.runtime = runtime_module
        self.type_ = type_
        super().__init__(parent)

    def run(self):
        if self.type_ == 'sms':
            self.result.emit(self.runtime.user_register(self.parent().input_email.text()))
        elif self.type_ == 'policy':
            self.result.emit({'message': self.runtime.get_policy()})
        elif self.type_ == 'verify':
            self.result.emit(self.runtime.user_verify(
                self.parent().input_email.text(), self.parent().input_verify_code.text(),
                hashlib.md5(str(self.parent().input_password.text()).encode("utf-8")).hexdigest()))


class Register(QWidget):
    def __init__(self, languages, configure, runtime_module):
        super().__init__()
        self.timeout = 60
        self.runtime = runtime_module
        self.languages = languages
        self.configure = configure
        self.setObjectName("Register")

        BodyLabel(languages[146], self).setGeometry(QRect(5, 5, 100, 35))
        self.input_email = LineEdit(self)
        self.input_email.setClearButtonEnabled(True)
        self.input_email.setGeometry(QRect(110, 5, 400, 35))

        BodyLabel(languages[150], self).setGeometry(QRect(5, 45, 100, 35))
        self.input_verify_code = LineEdit(self)
        self.input_verify_code.setClearButtonEnabled(True)
        self.input_verify_code.setGeometry(QRect(110, 45, 270, 35))
        self.click_verify_code = PrimaryPushButton(languages[151], self)
        self.click_verify_code.setGeometry(QRect(380, 45, 120, 35))
        self.click_verify_code.clicked.connect(self.get_verify_code)

        BodyLabel(languages[147], self).setGeometry(QRect(5, 80, 100, 35))
        self.input_password = PasswordLineEdit(self)
        self.input_password.setClearButtonEnabled(True)
        self.input_password.setGeometry(QRect(110, 80, 400, 35))

        policy = TextEdit(self)
        policy.setReadOnly(True)
        policy_thread = Loading(self, self.runtime, 'policy')
        policy_thread.result.connect(lambda message: policy.setMarkdown(message['message']))
        policy_thread.start()
        policy.setGeometry(QRect(0, 125, 620, 205))

        self.click_register = PrimaryPushButton(FluentIcon.SEND, languages[149], self)
        self.click_register.setGeometry(QRect(0, 345, 620, 35))
        self.click_register.clicked.connect(self.register)
        self.timeout_timer = QTimer(self)
        self.timeout_timer.timeout.connect(self._timeout_unlock)

    def _timeout_unlock(self):
        if self.timeout <= 0:
            self.timeout_timer.stop()
            self.click_verify_code.setText(self.languages[151])
            self.click_verify_code.setDisabled(False)
            self.timeout = 60
        else:
            self.click_verify_code.setText(str(self.timeout) + "s")
        self.timeout -= 1

    def pop(self, message: dict):
        if message['status']:
            widgets.pop_success(self, self.languages[149], message['message'])
        else:
            widgets.pop_error(self, self.languages[149], message['message'])

    def register(self):
        verify = Loading(self, self.runtime, 'verify')
        verify.result.connect(self.pop)
        verify.start()

    def get_verify_code(self):
        self.timeout_timer.start(1000)
        self.click_verify_code.setDisabled(True)
        sms = Loading(self, self.runtime, 'sms')
        sms.result.connect(self.pop)
        sms.start()
