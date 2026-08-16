import keyword
import builtins
import re

from PyQt5.Qt import Qt, QTextCharFormat, QFont, QRegExp, QSyntaxHighlighter, QColor


class BracketHighLighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bracket_formats = [
            QTextCharFormat(),
            QTextCharFormat(),
            QTextCharFormat(),
            QTextCharFormat(),
            QTextCharFormat(),
        ]
        colors = [Qt.red, Qt.green, Qt.blue, Qt.cyan, Qt.magenta]
        for i, color in enumerate(colors):
            self.bracket_formats[i].setForeground(color)
            self.bracket_formats[i].setFontWeight(QFont.Bold)

    def highlightBlock(self, text):
        stack = []
        for i, char in enumerate(text):
            if char in "([{":
                stack.append((char, i))
            elif char in ")]}":
                if stack:
                    opening_char, opening_index = stack.pop()
                    if (opening_char == '(' and char == ')') or \
                            (opening_char == '[' and char == ']') or \
                            (opening_char == '{' and char == '}'):
                        level = len(stack) % len(self.bracket_formats)
                        self.setFormat(opening_index, 1, self.bracket_formats[level])
                        self.setFormat(i, 1, self.bracket_formats[level])


class LoggingHighLighter(BracketHighLighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlightingRules = []

        log_time_format = QTextCharFormat()
        log_time_format.setForeground(Qt.darkMagenta)
        log_time_format.setFontWeight(QFont.Bold)
        pattern = QRegExp(r"\[\d{2}:\d{2}:\d{2}\]")
        rule = (pattern, log_time_format)
        self.highlightingRules.append(rule)

        # 添加 [INPUT] 高亮规则
        input_format = QTextCharFormat()
        input_format.setForeground(Qt.magenta)  # 紫色
        input_format.setFontWeight(QFont.Bold)
        input_pattern = QRegExp(r"\[WAITING\]")
        input_rule = (input_pattern, input_format)
        self.highlightingRules.append(input_rule)

    def highlightBlock(self, text):
        for pattern, format_ in self.highlightingRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format_)
                index = expression.indexIn(text, index + length)

        super().highlightBlock(text)
        self.setCurrentBlockState(0)


class PythonSyntaxHighlighter(BracketHighLighter):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.highlightingRules = []

        # 数字高亮
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("cyan"))
        self.highlightingRules.append((re.compile(r'\b\d+(\.\d+)?\b'), self.number_format))

        # 关键字高亮
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#FFA500"))
        keyword_format.setFontWeight(QFont.Bold)
        for word in keyword.kwlist:
            pattern = QRegExp("\\b" + word + "\\b")
            rule = (pattern, keyword_format)
            self.highlightingRules.append(rule)

        # 内置函数高亮
        builtin_function_format = QTextCharFormat()
        builtin_function_format.setForeground(QColor("#A020F0"))
        builtin_function_format.setFontWeight(QFont.Bold)
        builtin_functions = [func for func in dir(builtins) if callable(getattr(builtins, func))]
        for func in builtin_functions:
            pattern = QRegExp("\\b" + func + "\\b")
            rule = (pattern, builtin_function_format)
            self.highlightingRules.append(rule)

        single_line_comment_format = QTextCharFormat()
        single_line_comment_format.setForeground(Qt.gray)
        rule = (QRegExp("#[^\n]*"), single_line_comment_format)
        self.highlightingRules.append(rule)

        quotation_format = QTextCharFormat()
        quotation_format.setForeground(Qt.darkGreen)
        self.highlightingRules.append((QRegExp("\".*\""), quotation_format))
        self.highlightingRules.append((QRegExp("'.*'"), quotation_format))

    def highlightBlock(self, text):
        for pattern, format_ in self.highlightingRules:
            if isinstance(pattern, QRegExp):
                expression = pattern
                index = expression.indexIn(text)
                while index >= 0:
                    length = expression.matchedLength()
                    self.setFormat(index, length, format_)
                    index = expression.indexIn(text, index + length)
            elif isinstance(pattern, re.Pattern):
                for match in re.finditer(pattern, text):
                    start, end = match.span()
                    self.setFormat(start, end - start, format_)

        super().highlightBlock(text)
        self.setCurrentBlockState(0)
