from .sub_binding import login
from .sub_binding import register
from .sub_binding import upload

from PyQt5.Qt import QRect
from PyQt5.QtWidgets import QFrame, QStackedWidget, QWidget
from qfluentwidgets import Pivot


class Binding(QFrame):
    def __init__(self, languages, configure, runtime_module, add_interface):
        super().__init__()
        self.languages = languages
        self.configure = configure
        self.setObjectName("Binding")
        self.pivot_parameter = Pivot(self)
        self.stacked_widget = QStackedWidget(self)

        self.login_parameter = login.Login(languages, configure, runtime_module, add_interface)
        self.register_parameter = register.Register(languages, configure, runtime_module)
        self.upload_extension = upload.UploadExtensions(self, languages, configure, runtime_module)
        self.addSubInterface(self.login_parameter, "Login", self.languages[148])
        self.addSubInterface(self.register_parameter, "Register", self.languages[149])
        self.addSubInterface(self.upload_extension, "Upload", "开发者")

        self.pivot_parameter.setGeometry(QRect(10, 42, 100, 35))
        self.stacked_widget.setGeometry(QRect(30, 87, 630, 500))

        self.stacked_widget.setCurrentWidget(self.login_parameter)
        self.pivot_parameter.setCurrentItem(self.login_parameter.objectName())
        self.pivot_parameter.currentItemChanged.connect(
            lambda k: self.stacked_widget.setCurrentWidget(self.findChild(QWidget, k)))

    def addSubInterface(self, widget: QWidget, objectName, text):
        widget.setObjectName(objectName)
        self.stacked_widget.addWidget(widget)
        self.pivot_parameter.addItem(routeKey=objectName, text=text)
