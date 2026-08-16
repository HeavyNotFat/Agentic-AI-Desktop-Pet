from . import block


class BaseExceptionForFC:
    def __init__(self, pos_start, pos_end, message: str):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.message = message

    def as_string(self):
        current_line = self.pos_end.code.split('\n')[self.pos_end.line - 1]
        error_msg = (f"\033[91mTrackingException/s (the most recent call raised)\n"
                     f"  File '\x1B[4m\033[96m{self.pos_end.quote_file}\x1B[0m\033[91m', "
                     f"line {self.pos_end.line}, in '\033[96m{self.pos_end.quote_module}\033[91m'\n"
                     f"  \t{current_line}\n"
                     f"  \t{' ' * block.text_block_width(current_line[:self.pos_start.column])}"
                     f"{'^' * block.text_block_width(current_line[self.pos_start.column:self.pos_end.column])}\n"
                     f"\033[35m{self.__class__.__name__.replace('ForFC', '')}\033[0m: \033[93m{self.message}\033[0m")
        return error_msg


class SyntaxErrorForFC(BaseExceptionForFC):
    def __init__(self, pos_start, pos_end, message: str):
        super().__init__(pos_start, pos_end, message)


class RegistrationErrorForFC(BaseExceptionForFC):
    def __init__(self, pos_start, pos_end, message: str):
        super().__init__(pos_start, pos_end, message)


class ValueErrorForFC(BaseExceptionForFC):
    def __init__(self, pos_start, pos_end, message: str):
        super().__init__(pos_start, pos_end, message)


class TypeErrorForFC(BaseExceptionForFC):
    def __init__(self, pos_start, pos_end, message: str):
        super().__init__(pos_start, pos_end, message)


class NameErrorForFC(BaseExceptionForFC):
    def __init__(self, pos_start, pos_end, message: str):
        super().__init__(pos_start, pos_end, message)


class OverflowErrorForFC(BaseExceptionForFC):
    def __init__(self, pos_start, pos_end, message: str):
        super().__init__(pos_start, pos_end, message)


class ProgramInternalBugErrorForFC(BaseExceptionForFC):
    def __init__(self, pos_start, pos_end, message: str):
        super().__init__(pos_start, pos_end, message)


class FileNotFoundErrorForFC(BaseExceptionForFC):
    def __init__(self, pos_start, pos_end, message: str):
        super().__init__(pos_start, pos_end, message)


class RuntimeErrorForFC(BaseExceptionForFC):
    def __init__(self, pos_start, pos_end, message: str):
        super().__init__(pos_start, pos_end, message)
