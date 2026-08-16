if __name__ == "__main__":
    import core
else:
    from . import core

import os


def escape_python(string: str):
    string = string.replace("True", "true").replace("False", "false").replace("None", "null")
    return string


def run(codes):
    if not codes.strip(): return  None
    result = core.interpret(codes, True, "<Stdio Console>", "<Built-In>")
    if result is None: return None
    return result


if __name__ == "__main__":
    os.system("color 0")
    while True:
        print(run(input(">>> ")))

