from time import strftime
from .customize import highlight

from PyQt5.Qt import QRect, Qt, QEventLoop, pyqtSignal, QFont, QFontDatabase, QTextCursor
from PyQt5.QtWidgets import QFrame
from qfluentwidgets import TextEdit, ComboBox, LineEdit, ToolButton, FluentIcon


class DeveloperOptions(QFrame):
    input_finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setObjectName("DeveloperOptions")

        self.input_result = None
        self.current_waiting_id = None
        self.is_pressed = False
        self.input_lists = []
        self.input_id = 1

        font_id = QFontDatabase.addApplicationFont("./interface/setting/sub_general/JetBrainsMono-Bold.ttf")
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        jetbrains_mono = QFont(font_families[0], 10)
        self.input_logger = TextEdit(self)
        self.input_logger.setFont(jetbrains_mono)
        self.input_logger.setReadOnly(True)
        self.input_logger.setGeometry(QRect(0, 42, 640, 440))
        self.input_logger.setLineWrapMode(0)
        self.input_logger.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.highlighter = highlight.LoggingHighLighter(self.input_logger.document())

        self.select_reply = ComboBox(self)
        self.select_reply.setGeometry(QRect(0, 482, 100, 30))
        self.input_message = LineEdit(self)
        self.input_message.setGeometry(QRect(100, 482, 450, 30))
        self.click_send = ToolButton(FluentIcon.SEND, self)
        self.click_send.clicked.connect(self.send)
        self.click_send.setGeometry(QRect(550, 482, 90, 36))

    def send(self):
        selected_id = self.select_reply.currentText()
        if selected_id == self.current_waiting_id:
            self.input_result = self.input_message.text()
            self.input_finished.emit()
            index = self.select_reply.findText(selected_id)
            if index >= 0:
                self.select_reply.removeItem(index)
            self.current_waiting_id = None
        self.is_pressed = selected_id

    def print_(self, *args, end="\n"):
        print(*args, end=end)
        self.input_logger.insertPlainText(f"[{strftime('%H:%M:%S')}]  ")
        for argument in args:
            self.input_logger.insertPlainText(str(argument))
            self.input_logger.insertPlainText(" ")
        self.input_logger.insertPlainText(end)
        self.input_logger.moveCursor(QTextCursor.End)

    def input_(self, msg=""):
        self.input_logger.insertPlainText(f"{self.input_id}. [WAITING] [{strftime('%H:%M:%S')}]  ")
        self.input_logger.insertPlainText(str(msg))

        id_ = f"{self.input_id} [{strftime('%H:%M:%S')}]"
        self.input_message.setPlaceholderText(str(msg))
        self.select_reply.addItem(id_)
        self.input_lists.append(id_)
        self.input_id += 1

        self.current_waiting_id = id_
        self.input_result = None

        loop = QEventLoop()
        self.input_finished.connect(loop.quit)
        loop.exec_()

        self.input_logger.insertPlainText(f"{self.input_result}\n")
        self.input_message.clear()
        self.is_pressed = False
        return self.input_result

