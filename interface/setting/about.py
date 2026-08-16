from .customize import widgets

from PyQt5.Qt import QRect, QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget
from qfluentwidgets import PushSettingCard, FluentIcon, TextEdit


class CheckUpdate(QThread):
    is_latest = pyqtSignal(str)
    is_error = pyqtSignal(bool)

    def __init__(self, parent, runtime_module):
        super().__init__(parent)
        self.runtime_module = runtime_module

    def run(self):
        is_latest = self.runtime_module.check_update()
        if is_latest is True:
            self.is_latest.emit("latest")
        elif isinstance(is_latest, str):
            self.is_latest.emit(is_latest)
        elif is_latest is None:
            self.is_error.emit(True)


class RefreshNoticeBoard(QThread):
    result = pyqtSignal(str)

    def __init__(self, parent, runtime_module):
        super().__init__(parent)
        self.runtime_module = runtime_module

    def run(self):
        notice_board = self.runtime_module.get_notice_board()
        self.result.emit(notice_board)


class About(QWidget):
    def __init__(self, languages, runtime_module):
        super().__init__()
        self.languages = languages
        self.runtime_module = runtime_module
        self.setObjectName("About")

        self.check_update = PushSettingCard(
            text=self.languages[102],
            icon=FluentIcon.UPDATE,
            title=self.languages[102],
            content=self.languages[103],
            parent=self,
        )
        self.check_update.clicked.connect(self.check_if_latest)
        self.check_update.setGeometry(QRect(10, 52, 630, 100))
        self.show_notice_board = TextEdit(self)
        self.show_notice_board.setLineWrapMode(0)
        self.show_notice_board.setReadOnly(True)
        self.show_notice_board.setGeometry(QRect(10, 132, 630, 300))

        self.license_text = TextEdit(self)
        self.license_text.setReadOnly(True)
        self.license_text.setGeometry(QRect(10, 442, 630, 80))
        self.license_text.setText(open("./resources/license", "r", encoding="utf-8").read())

        refresh_notice_board = RefreshNoticeBoard(self, self.runtime_module)
        refresh_notice_board.result.connect(self.refresh_notice_board)
        refresh_notice_board.start()

    def refresh_notice_board(self, text):
        self.show_notice_board.setMarkdown(text)

    def check_if_latest(self):
        def _is_latest(is_latest):
            self.check_update.button.setText(self.languages[102])
            if is_latest == "latest":
                widgets.pop_success(self, self.languages[104], self.languages[104])
                self.check_update.contentLabel.setText(self.languages[104])
            else:
                widgets.pop_warning(self, self.languages[105].format(latest=is_latest),
                                    self.languages[105].format(latest=is_latest))
                self.check_update.contentLabel.setText(self.languages[105].format(latest=is_latest))

        def _is_error(is_error):
            self.check_update.button.setText(self.languages[102])
            if is_error:
                widgets.pop_warning(self, self.languages[106], self.languages[106])
                self.check_update.contentLabel.setText(self.languages[106])

        self.check_update.button.setText(self.languages[107])
        update_checker = CheckUpdate(self, self.runtime_module)
        update_checker.is_latest.connect(_is_latest)
        update_checker.is_error.connect(_is_error)
        update_checker.start()
