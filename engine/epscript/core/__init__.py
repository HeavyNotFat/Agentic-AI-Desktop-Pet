from . import interpreter
from . import exception


def interpret(syntax: str, support_chinese_keyword: bool, quote_file: str, quote_module: str):
    interpreted = interpreter.run(syntax, support_chinese_keyword, quote_file, quote_module)
    if isinstance(interpreted, exception.BaseExceptionForFC): return interpreted.as_string()
    if hasattr(interpreted.value, "show_value"): return interpreted.value.show_value
    elif interpreted.value is None: return None
    else:
        if not hasattr(interpreted.value, "__iter__"):
            if isinstance(interpreted.value, interpreter.BaseNullCallBackButValue): return None
            else: return str(interpreted.value)
        result = []
        for value in interpreted.value:
            if isinstance(value, interpreter.BaseNullCallBackButValue):
                continue
            else:
                result.append(str(value))
        if result:
            return '\n'.join(result)
        return None
