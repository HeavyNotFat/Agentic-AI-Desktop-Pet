import typing

from . import tokens
from .. import exception

SYMBOL_MATCH_DIGITS = "0123456789"
SYMBOL_MATCH_STRING = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
SYMBOL_MARKS = "~`!@#$%^&*()+-={}|[]:\\\";'<>?,./！￥……（）——【】「」“”‘’：；《》，。、？·"


class Position:
    def __init__(self, index, column, line, code, quote_file, quote_module):
        self.index = index
        self.column = column
        self.line = line
        self.code = code
        self.quote_file = quote_file
        self.quote_module = quote_module

    def advance(self):
        self.index += 1
        self.column += 1

        return self

    def copy(self):
        return Position(self.index, self.column, self.line, self.code, self.quote_file, self.quote_module)


class Token:
    def __init__(self, type_, value: typing.Any | None=None, addition: typing.Any | None=None,
                 pos_start: Position | None = None, pos_end: Position | None = None):
        self.type = type_
        self.value = value
        self.addition = addition

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end

    def matches(self, type_, value):
        return self.type == type_ and self.value == value

    def __repr__(self):
        if self.value is None:
            return f'{self.type}'
        else:
            return f'{self.type}:{self.value}'


class Lexer:
    def __init__(self, text, support_chinese_keyword: bool = False,
                 quote_file: str = "<Stdio Console>", quote_module: str = "<Built-In>"):
        self.chinese_keyword = support_chinese_keyword
        self.text = text

        self.pos = Position(-1, -1, 1, text, quote_file, quote_module)
        self.current_char = None

        self.advance()

    def advance(self) -> None:
        self.pos.advance()
        self.current_char = self.text[self.pos.index] if self.pos.index < len(self.text) else None

    def make_token(self) -> tuple[exception.BaseExceptionForFC | None, list[Token]]:
        token: list[Token] = []

        while self.current_char is not None:
            # 令牌处理
            if self.current_char == '\n':
                self.pos.line += 1
                self.pos.column = 0
                token.append(Token(tokens.NEWLINE, pos_start=self.pos.copy()))
            elif self.current_char in " \t\r\a":
                pass
            elif self.current_char in SYMBOL_MATCH_DIGITS:
                exception_returned, token_returned = self._make_numbers()
                if exception_returned is not None:
                    return exception_returned, []
                token.append(token_returned)
                continue
            elif self.current_char in ("\"", "'") or (self.chinese_keyword and self.current_char in ("“", "‘")):
                exception_returned, token_returned = self._make_string(self.current_char)
                if exception_returned is not None:
                    return exception_returned, []
                token.append(token_returned)
                continue
            elif self.current_char == "." or (self.chinese_keyword and self.current_char == "。"):
                token.append(Token(tokens.DOT, pos_start=self.pos.copy()))
            elif self.current_char == "(" or (self.chinese_keyword and self.current_char == "（"):
                token.append(Token(tokens.LEFT_PARENT, pos_start=self.pos.copy()))
            elif self.current_char == ")" or (self.chinese_keyword and self.current_char == "）"):
                token.append(Token(tokens.RIGHT_PARENT, pos_start=self.pos.copy()))
            elif self.current_char == "[" or (self.chinese_keyword and self.current_char == "【"):
                token.append(Token(tokens.LEFT_BRACKET, pos_start=self.pos.copy()))
            elif self.current_char == "]" or (self.chinese_keyword and self.current_char == "】"):
                token.append(Token(tokens.RIGHT_BRACKET, pos_start=self.pos.copy()))
            elif self.current_char == "{" or (self.chinese_keyword and self.current_char == "「"):
                token.append(Token(tokens.LEFT_FLAG, pos_start=self.pos.copy()))
            elif self.current_char == "}" or (self.chinese_keyword and self.current_char == "」"):
                token.append(Token(tokens.RIGHT_FLAG, pos_start=self.pos.copy()))
            elif self.current_char == "," or (self.chinese_keyword and self.current_char == "，"):
                token.append(Token(tokens.COMMA, pos_start=self.pos.copy()))
            elif self.current_char == "+":
                token.append(Token(tokens.PLUS, pos_start=self.pos.copy()))
            elif self.current_char == "-":
                token.append(Token(tokens.MINUS, pos_start=self.pos.copy()))
            elif self.current_char == "*":
                self.advance()
                if self.current_char == "*":
                    token.append(Token(tokens.POW, pos_start=self.pos.copy()))
                    self.advance()
                else:
                    token.append(Token(tokens.MULTIPLY, pos_start=self.pos.copy()))
                continue
            elif self.current_char == "/":
                token.append(Token(tokens.DIVIDE, pos_start=self.pos.copy()))
            elif self.current_char == "%":
                token.append(Token(tokens.MOD, pos_start=self.pos.copy()))
            elif self.current_char == "=":
                self.advance()
                if self.current_char == "=":
                    token.append(Token(tokens.EQUAL, pos_start=self.pos.copy()))
                    self.advance()
                else:
                    token.append(Token(tokens.COPY, pos_start=self.pos.copy()))
                continue
            elif self.current_char == ">" or (self.chinese_keyword and self.current_char == "》"):
                self.advance()
                if self.current_char == "=":
                    token.append(Token(tokens.GREATER_EQUAL, pos_start=self.pos.copy()))
                    self.advance()
                else:
                    token.append(Token(tokens.GREATER, pos_start=self.pos.copy()))
                continue
            elif self.current_char == "<" or (self.chinese_keyword and self.current_char == "《"):
                self.advance()
                if self.current_char == "=":
                    token.append(Token(tokens.LESSER_EQUAL, pos_start=self.pos.copy()))
                    self.advance()
                else:
                    token.append(Token(tokens.LESSER, pos_start=self.pos.copy()))
                continue
            elif self.current_char == "!" or (self.chinese_keyword and self.current_char == "！"):
                self.advance()
                if self.current_char == "=":
                    token.append(Token(tokens.NOT_EQUAL, pos_start=self.pos.copy()))
                    self.advance()
                else:
                    token.append(Token(tokens.NOT, pos_start=self.pos.copy()))
                continue
            elif self.current_char == "&":
                token.append(Token(tokens.AND, pos_start=self.pos.copy()))
            elif self.current_char == "|":
                token.append(Token(tokens.OR, pos_start=self.pos.copy()))
            elif self.current_char == ":" or (self.chinese_keyword and self.current_char == "："):
                token.append(Token(tokens.ONION, pos_start=self.pos.copy()))
            elif self.current_char == ";" or (self.chinese_keyword and self.current_char == "；"):
                token.append(Token(tokens.NEWLINE, pos_start=self.pos.copy()))
            elif self.current_char == "#":
                self.skip_comments()
            else:
                origin = self.current_char
                token.append(self._make_literal())
                if origin == self.current_char:
                    end_pos = Position(self.pos.index, self.pos.column + 1, self.pos.line, self.pos.code,
                                       self.pos.quote_file, self.pos.quote_module)
                    return exception.RegistrationErrorForFC(self.pos.copy(), end_pos,
                                                            f"Non-registered symbol '{origin}'"), []
                continue
            self.advance()

        token.append(Token(tokens.EOF, pos_start=self.pos.copy()))
        return None, token

    def skip_comments(self) -> None:
        self.advance()
        while self.current_char is not None and self.current_char != "#" and self.current_char != "\n":
            self.advance()

    def _make_literal(self) -> Token:
        literal_char = ""
        pos_start = self.pos.copy()

        while self.current_char is not None and self.current_char not in SYMBOL_MARKS + " \t\n\r\a":
            literal_char += self.current_char
            self.advance()

        if self.chinese_keyword and (literal_char in tokens.KWLIST_ZH or literal_char in tokens.KWLIST_EN):
            return Token(tokens.KEYWORD, literal_char, pos_start=pos_start, pos_end=self.pos.copy())
        elif not self.chinese_keyword and literal_char in tokens.KWLIST_EN:
            return Token(tokens.KEYWORD, literal_char, pos_start=pos_start, pos_end=self.pos.copy())
        else:
            return Token(tokens.VARIABLE, literal_char, pos_start=pos_start, pos_end=self.pos.copy())

    def _make_string(self, end_symbol: str) -> tuple[exception.BaseExceptionForFC | None, Token | None]:
        start_pos = self.pos.copy()
        string_char = ""
        if self.chinese_keyword:
            if end_symbol == "“": end_symbol = "”"
            elif end_symbol == "‘": end_symbol = "’"

        self.advance()
        while self.current_char != end_symbol:
            if self.current_char is None:
                return exception.SyntaxErrorForFC(
                    start_pos, self.pos,
                    f"String is not closed, did you forget {'\'"\'' if end_symbol == '"' else "\"'\""}?"), None
            escape_start_pos = self.pos.copy()
            if self.current_char == "\\":
                self.advance()
                if self.current_char == "n":
                    string_char += "\n"
                elif self.current_char == "t":
                    string_char += "\t"
                elif self.current_char == "\\":
                    string_char += "\\"
                elif self.current_char == "\"":
                    string_char += "\""
                elif self.current_char == "'":
                    string_char += "\'"
                else:
                    return exception.SyntaxErrorForFC(
                        escape_start_pos, self.pos.copy(),
                        f"Unknown escape character '{self.current_char}',"
                        f" supported for 'n', 't', '\\', '\"', '\''"), None
                self.advance()
                continue
            string_char += self.current_char
            self.advance()
            if self.current_char == end_symbol:
                self.advance()
                break
        return None, Token(tokens.STRING, string_char, pos_start=start_pos, pos_end=self.pos)

    def _make_numbers(self) -> tuple[exception.BaseExceptionForFC | None, Token | None]:
        start_pos = self.pos.copy()
        digits_char = ""
        dot_count = 0
        prec_count = 0

        while self.current_char is not None and self.current_char in SYMBOL_MATCH_DIGITS + "." + \
                ("。" if self.chinese_keyword else ""):
            if self.current_char == ".":
                if dot_count == 1:
                    start_pos = self.pos.copy()
                dot_count += 1
            if dot_count == 1:
                prec_count += 1
            digits_char += self.current_char
            self.advance()
        if dot_count == 1:
            return None, Token(tokens.FLOAT, digits_char, prec_count, pos_start=start_pos, pos_end=self.pos)
        elif dot_count == 0:
            return None, Token(tokens.INT, digits_char, pos_start=start_pos, pos_end=self.pos)
        else:
            return exception.SyntaxErrorForFC(start_pos, self.pos, "Invalid number for multi-digit float"), None
