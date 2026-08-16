import keyword
import builtins
import inspect
from typing import Literal

from . import highlight

from PyQt5.Qt import Qt, QStringListModel, QStandardItemModel, QFont, QIcon, QStandardItem, QTimer, QFontDatabase
from PyQt5.QtWidgets import QCompleter, QComboBox, QVBoxLayout
from qfluentwidgets import TextEdit, InfoBar, InfoBarPosition, MessageBox, IconWidget, ImageLabel, \
    CaptionLabel, ElevatedCardWidget


class SimpleCard(ElevatedCardWidget):
    def __init__(self, icon, name: str, parent=None):
        super().__init__(parent)
        if isinstance(icon, str):
            self.iconWidget = ImageLabel(icon, self)
        else:
            self.iconWidget = IconWidget(icon)
        self.label = CaptionLabel(name, self)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignCenter)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.iconWidget, 0, Qt.AlignCenter)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.label, 0, Qt.AlignHCenter | Qt.AlignBottom)

        self.setFixedSize(70, 70)
        self.iconWidget.setFixedSize(30, 30)


class CodeEdit(TextEdit):
    def __init__(self, interface, parent=None):
        super().__init__(parent)
        font_id = QFontDatabase.addApplicationFont("./interface/setting/sub_general/JetBrainsMono-Bold.ttf")
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        jetbrains_mono = QFont(font_families[0], 10)
        self.setFont(jetbrains_mono)
        self.setLineWrapMode(0)
        self.highlighter = highlight.PythonSyntaxHighlighter(self.document())

        self.interface = interface
        self.completer = QCompleter()
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)

        self.model = QStringListModel()
        self.completer.setModel(self.model)

        self.combo_completer = QComboBox()
        self.combo_completer.setStyleSheet("""
        QComboBox {
            border: 1px solid #3f3f3f;
            padding: 2px 4px;
            font-size: 14px;
            background-color: #1e1e1e;
            color: #cccccc;
        }
    
        QComboBox:focus {
            border: 1px solid #007acc; /* VS Code focus color */
        }
    
        QComboBox::drop-down {
            border-left: 1px solid #3f3f3f;
            width: 20px;
        }
    
        QComboBox::down-arrow {
            width: 8px;
            height: 8px;
        }
    
        QComboBox QAbstractItemView {
            border: 1px solid #3f3f3f;
            background-color: #1e1e1e;
            selection-background-color: #007acc;
            color: #cccccc;
        }
    
        QComboBox QAbstractItemView:item {
            padding: 4px 8px;
        }
        """)
        self.combo_completer.setFont(QFont("微软雅黑", 11))
        self.combo_completer.setEditable(False)
        self.combo_completer.setModel(self.model)
        self.combo_completer.hide()
        self.combo_completer.activated.connect(self.click_complete)

        layout = QVBoxLayout()
        layout.addWidget(self.combo_completer)
        self.setLayout(layout)

        self.textChanged.connect(self.update_completions)
        self.cursorPositionChanged.connect(self.update_completions)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Tab:
            if self.combo_completer.isVisible():
                self.insert_completion(self.combo_completer.currentIndex())
                self.combo_completer.hide()
            else:
                self.insertPlainText("    ")
        elif event.key() == Qt.Key_Down:
            if self.combo_completer.isVisible():
                index = self.combo_completer.currentIndex()
                if index < self.combo_completer.count() - 1:
                    self.combo_completer.setCurrentIndex(index + 1)
            else:
                super().keyPressEvent(event)
        elif event.key() == Qt.Key_Up:
            if self.combo_completer.isVisible():
                index = self.combo_completer.currentIndex()
                if index > 0:
                    self.combo_completer.setCurrentIndex(index - 1)
            else:
                super().keyPressEvent(event)
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            cursor = self.textCursor()
            block = cursor.block()
            text = block.text()

            previous_text = block.text()
            indent = len(previous_text) - len(previous_text.lstrip())
            if text.strip().endswith(':'):
                self.insertPlainText("\n" + " " * indent + "    ")
            else:
                self.insertPlainText("\n" + " " * indent)
        elif event.key() == Qt.Key_Escape:
            self.combo_completer.hide()
        elif event.key() == Qt.Key_Period:
            self.update_completions()
            super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    @staticmethod
    def get_keywords():
        return keyword.kwlist

    @staticmethod
    def get_other():
        builtin_functions = [func for func in dir(builtins) if callable(getattr(builtins, func))]
        builtin_functions.append("interface")
        return builtin_functions

    def update_completions(self):
        def get_completions(module_, parts_, current_prefix):
            if not parts_:
                return

            first_part = parts_[0]
            remaining_parts = parts_[1:]

            for m in dir(module_):
                if m[0] == "_":
                    continue
                if m.startswith(first_part):
                    attr = getattr(module_, m, None)
                    if not remaining_parts:
                        if inspect.ismodule(attr):
                            filtered_list.append((f"{current_prefix}.{m}", "module", m))
                        elif inspect.isclass(attr):
                            filtered_list.append((f"{current_prefix}.{m}", "class", m))
                        elif callable(attr):
                            filtered_list.append((f"{current_prefix}.{m}", "function", m))
                        else:
                            filtered_list.append((f"{current_prefix}.{m}", "variable", m))
                    else:
                        if attr:
                            get_completions(attr, remaining_parts, f"{current_prefix}.{m}")

        cursor = self.textCursor()
        block = cursor.block()
        text = block.text()
        pos = cursor.positionInBlock()

        start = pos - 1
        while start >= 0 and (text[start].isalnum() or text[start] == '.'):
            start -= 1
        start += 1
        prefix = text[start:pos]

        if len(prefix) < 2:
            self.combo_completer.hide()
            return

        parts = prefix.split('.')
        filtered_list = []

        if len(parts) == 1:
            for word in self.get_keywords():
                if word.startswith(prefix):
                    filtered_list.append((word, "keyword", word))
            for word in self.get_other():
                if word.startswith(prefix):
                    filtered_list.append((word, "variable", word))
        else:
            module_name = parts[0]
            if module_name == "interface":
                module = self.interface
            elif module_name == "builtins":
                module = builtins
            else:
                module = None

            if module:
                get_completions(module, parts[1:], module_name)

        item_model = QStandardItemModel()
        for full_path, item_type, display_text in filtered_list:
            icon = QIcon(f"./resources/static/{item_type}.png")
            q_item = QStandardItem(icon, display_text)
            q_item.setData(full_path, Qt.UserRole)
            item_model.appendRow(q_item)

        self.combo_completer.setModel(item_model)

        if not filtered_list:
            self.combo_completer.hide()
            return

        rect = self.cursorRect(cursor)
        rect.setX(0)
        rect.setY(rect.y() + 25)
        rect.setHeight(25)
        rect.setWidth(500)
        self.combo_completer.setGeometry(rect)
        self.combo_completer.show()

    def click_complete(self, completion):
        self.insert_completion(completion)
        QTimer.singleShot(50, self.setFocus)

    def insert_completion(self, completion):
        if isinstance(completion, int):
            completion = self.combo_completer.itemData(completion, Qt.UserRole)
        tc = self.textCursor()
        block = tc.block()
        text = block.text()
        pos = tc.positionInBlock()

        start = pos - 1
        while start >= 0 and (text[start].isalnum() or text[start] == '.'):
            start -= 1
        start += 1

        tc.setPosition(block.position() + start)
        tc.movePosition(tc.Right, tc.KeepAnchor, pos - start)
        tc.insertText(completion)
        self.setTextCursor(tc)


def pop_message(parent, title: str, content: str, yes_text: str = "OK", no_text: str = "Cancel"):
    w = MessageBox(
        title,
        content,
        parent
    )
    w.yesButton.setText(yes_text)
    w.cancelButton.setText(no_text)

    return w.exec()


def pop_warning(parent, title, content, duration=1200, orient=Qt.Horizontal):
    InfoBar.warning(
        title=title,
        content=content,
        orient=orient,
        isClosable=True,
        position=InfoBarPosition.TOP,
        duration=duration,
        parent=parent
    )


def pop_success(parent, title, content, duration=1200, orient=Qt.Horizontal):
    InfoBar.success(
        title=title,
        content=content,
        orient=orient,
        isClosable=True,
        position=InfoBarPosition.TOP,
        duration=duration,
        parent=parent
    )


def pop_error(parent, title, content, duration=2000, orient=Qt.Horizontal):
    InfoBar.error(
        title=title,
        content=content,
        orient=orient,
        isClosable=True,
        position=InfoBarPosition.TOP,
        duration=duration,
        parent=parent
    )


def pop_info(parent, title, content, duration=2000, orient=Qt.Horizontal):
    InfoBar.info(
        title=title,
        content=content,
        orient=orient,
        isClosable=True,
        position=InfoBarPosition.TOP,
        duration=duration,
        parent=parent
    )


def pop_notification(title, content, type_: Literal['error', 'warning', 'success', 'info'], duration=2500):
    """
    弹出消息
    :param title: 标题
    :param content: 内容（正文）
    :param type_: 类型（错误弹窗，警告弹窗，成功弹窗）
    :param duration: 持续时间（毫秒）
    """
    if type_ == "error":
        func = InfoBar.error
    elif type_ == "warning":
        func = InfoBar.warning
    elif type_ == "success":
        func = InfoBar.success
    else:
        func = InfoBar.info
    func(
        title=title,
        content=content,
        orient=Qt.Vertical,
        position=InfoBarPosition.BOTTOM_RIGHT,
        duration=duration,
        parent=InfoBar.desktopView()
    )
