import os
import pathlib
import decimal
import traceback
from abc import abstractmethod

from .. import token
from .. import parser
from .. import exception
from ..parser.nodes import FunctionCallNode


class RuntimeResult:
    def __init__(self):
        self.value = None
        self.error = None
        self.func_return_value = None
        self.loop_should_continue = False
        self.loop_should_break = False

    def reset(self):
        self.value = None
        self.error = None
        self.func_return_value = None
        self.loop_should_continue = False
        self.loop_should_break = False

    def register(self, res):
        self.error = res.error
        self.func_return_value = res.func_return_value
        self.loop_should_continue = res.loop_should_continue
        self.loop_should_break = res.loop_should_break
        return res.value

    def success(self, value):
        self.reset()
        self.value = value
        return self

    def success_return(self, value):
        self.reset()
        self.func_return_value = value
        return self

    def success_continue(self):
        self.reset()
        self.loop_should_continue = True
        return self

    def success_break(self):
        self.reset()
        self.loop_should_break = True
        return self

    def failure(self, error):
        self.reset()
        self.error = error
        return self

    def should_return(self):
        return (
                self.error or
                self.func_return_value or
                self.loop_should_continue or
                self.loop_should_break
        )


class SymbolTable:
    def __init__(self, parent=None):
        """
        Structure:
            {'name': attribute, 'class': [attribute, {<objects>}]}
        """
        self.symbol_table = {}
        self.parent = parent

    def set(self, name, value):
        self.symbol_table[name] = value

    def get(self, name):
        value = self.symbol_table.get(name)
        if value is None and self.parent:
            value = self.parent.get(name)
        return value


class BaseDataStructure:
    def __init__(self, child):
        self.child = child
        self.start_pos = self.end_pos = None

    def add_to(self, other):
        return None, RuntimeResult().failure(exception.TypeErrorForFC(
            self.child.start_pos, other.end_pos,
            f"Unsupported operator '+' for '{type(self.child).__name__}' and '{type(other).__name__}'"))

    def sub_by(self, other):
        return None, RuntimeResult().failure(exception.TypeErrorForFC(
            self.child.start_pos, other.end_pos,
            f"Unsupported operator '-' for '{type(self.child).__name__}' and '{type(other).__name__}'"))

    def mul_by(self, other):
        return None, RuntimeResult().failure(exception.TypeErrorForFC(
            self.child.start_pos, other.end_pos,
            f"Unsupported operator '*' for '{type(self.child).__name__}' and '{type(other).__name__}'"))

    def div_by(self, other):
        return None, RuntimeResult().failure(exception.TypeErrorForFC(
            self.child.start_pos, other.end_pos,
            f"Unsupported operator '/' for '{type(self.child).__name__}' and '{type(other).__name__}'"))

    def pow_by(self, other):
        return None, RuntimeResult().failure(exception.TypeErrorForFC(
            self.child.start_pos, other.end_pos,
            f"Unsupported operator '**' for '{type(self.child).__name__}' and '{type(other).__name__}'"))

    def mod_by(self, other):
        return None, RuntimeResult().failure(exception.TypeErrorForFC(
            self.child.start_pos, other.end_pos,
            f"Unsupported operator '%' for '{type(self.child).__name__}' and '{type(other).__name__}'"))

    def eq_to(self, other):
        return Boolean(self.child.value == other.value).set_pos(self.child.start_pos, other.end_pos), None

    def ne_to(self, other):
        return Boolean(self.child.value != other.value).set_pos(self.child.start_pos, other.end_pos), None

    def gt_to(self, other):
        return None, RuntimeResult().failure(exception.TypeErrorForFC(
            self.child.start_pos, other.end_pos,
            f"Unsupported operator '>' for '{type(self.child).__name__}' and '{type(other).__name__}'"))

    def lt_to(self, other):
        return None, RuntimeResult().failure(exception.TypeErrorForFC(
            self.child.start_pos, other.end_pos,
            f"Unsupported operator '<' for '{type(self.child).__name__}' and '{type(other).__name__}'"))

    def gte_to(self, other):
        return None, RuntimeResult().failure(exception.TypeErrorForFC(
            self.child.start_pos, other.end_pos,
            f"Unsupported operator '>=' for '{type(self.child).__name__}' and '{type(other).__name__}'"))

    def lte_to(self, other):
        return None, RuntimeResult().failure(exception.TypeErrorForFC(
            self.child.start_pos, other.end_pos,
            f"Unsupported operator '<=' for '{type(self.child).__name__}' and '{type(other).__name__}'"))

    def sub_block(self, from_, to, step):
        return None, RuntimeResult().failure(exception.TypeErrorForFC(
            self.child.start_pos, self.child.end_pos,
            f"Unsupported operator sub-block for '{type(self.child).__name__}'"))

    @abstractmethod
    def is_true(self):
        return Boolean(None)

    def set_pos(self, start_pos=None, end_pos=None):
        self.start_pos = start_pos
        self.end_pos = end_pos

        return self


class BaseNullCallBackButValue(BaseDataStructure):
    def __init__(self, copy_value):
        super().__init__(self)
        self.value = None
        self.copy_value = copy_value

    def is_true(self):
        return False


class BaseFunction(BaseDataStructure):
    def __init__(self, name):
        super().__init__(self)
        self.name = name or "<anonymous>"

    @staticmethod
    def generate_new_context(parent_symbol):
        new_symbol = SymbolTable(parent_symbol)
        return new_symbol

    def check_args(self, arg_names, args):
        res = RuntimeResult()

        if len(args) > len(arg_names):
            return res.failure(exception.TypeErrorForFC(
                self.start_pos, self.end_pos,
                f"{len(args) - len(arg_names)} too many args passed into {self}",
            ))

        if len(args) < len(arg_names):
            return res.failure(exception.TypeErrorForFC(
                self.start_pos, self.end_pos,
                f"{len(arg_names) - len(args)} too few args passed into {self}",
            ))

        return res.success(BaseNullCallBackButValue(None))

    @staticmethod
    def populate_args(arg_names, args, new_symbol):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            new_symbol.set(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, new_symbol):
        res = RuntimeResult()
        res.register(self.check_args(arg_names, args))
        if res.should_return(): return res
        self.populate_args(arg_names, args, new_symbol)
        return res.success(BaseNullCallBackButValue(None))

    def is_true(self):
        return True

    @abstractmethod
    def copy(self):
        pass


class Function(BaseFunction):
    def __init__(self, name, body_node, arg_names, support_chinese, father_call):
        super().__init__(name)
        self.value = f"<Function {self.name} @ self>"
        self.show_value = None
        self.body_node = body_node
        self.arg_names = arg_names
        self.support_chinese = support_chinese
        self.father_call = father_call

    def execute(self, args, parent_symbol):
        res = RuntimeResult()
        interpreter = Interpreter()
        exec_ctx = self.generate_new_context(parent_symbol)

        res.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
        if res.should_return(): return res

        res.register(interpreter.visit(self.body_node, exec_ctx, self.support_chinese, self.father_call))

        if res.should_return() and res.func_return_value is None: return res
        ret_value = res.func_return_value or Boolean(None)
        return res.success(ret_value)

    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_names, self.support_chinese, self.father_call)
        copy.set_pos(self.start_pos, self.end_pos)
        return copy

    def __repr__(self):
        return f"<Function {self.name} @ self>"


class BuiltinFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)
        self.value = f"<Built-in Function {self.name} @ self>"

    def execute(self, args, parent_symbol):
        res = RuntimeResult()
        symbol = self.generate_new_context(parent_symbol)

        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_visit_method)

        res.register(self.check_and_populate_args(method.arg_names, args, symbol))
        if res.should_return(): return res

        return_value = res.register(method(symbol))
        if res.should_return(): return res
        return res.success(return_value)

    def no_visit_method(self, node, symbol):
        raise Exception(f'No execute_{self.name} method defined')

    def execute_output(self, symbol):
        if isinstance(symbol.get('content'), BaseNullCallBackButValue):
            return RuntimeResult().success(BaseNullCallBackButValue(Boolean(None)))
        else:
            print(str(symbol.get('content').value))
        return RuntimeResult().success(BaseNullCallBackButValue(Boolean(None)))
    execute_output.arg_names = ['content']

    def execute_output_cnkeyword(self, symbol):
        return self.execute_output(symbol)
    execute_output_cnkeyword.arg_names = ['content']

    def execute_readline(self, symbol):
        return RuntimeResult().success(String(input(symbol.get("content"))))
    execute_readline.arg_names = ['content']

    def execute_readline_cnkeyword(self, symbol):
        return self.execute_readline(symbol)
    execute_readline_cnkeyword.arg_names = ['content']

    def execute_run(self, symbol):
        filename = symbol.get('filename')
        if not isinstance(filename, String):
            return RuntimeResult().failure(exception.TypeErrorForFC(
                self.start_pos, self.end_pos,
                f"The argument 'filename' must be 'String', not '{type(filename).__name__}'"))
        filename = filename.value
        if not os.path.exists(filename):
            return RuntimeResult().failure(exception.FileNotFoundErrorForFC(
                self.start_pos, self.end_pos,
                f"File {filename} does not exist"))
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
            f.close()

        interpreted_ = run(code, pathlib.Path(filename).suffix.lower() == ".epsc",
                         filename, self.start_pos.quote_module, symbol)
        if isinstance(interpreted_, exception.BaseExceptionForFC): return RuntimeResult().failure(
            exception.RuntimeErrorForFC(
                self.start_pos, self.end_pos,
                f"Failed to run script '{filename}'\n\n"
                f"\033[35mBecause\033[0m: \033[91m\n{interpreted_.as_string()}\033[0m"
            )
        )
        else:
            return RuntimeResult().success(BaseNullCallBackButValue(None))
    execute_run.arg_names = ['filename']

    def execute_run_cnkeyword(self, symbol):
        return self.execute_run(symbol)
    execute_run_cnkeyword.arg_names = ['filename']

    def execute_Integer(self, symbol):
        try:
            return RuntimeResult().success(Integer(int(symbol.get('value').value)))
        except (ValueError, TypeError):
            return RuntimeResult().failure(exception.TypeErrorForFC(
                self.start_pos, self.end_pos,
                f"The argument 'value' can not convert to 'Integer'"))
    execute_Integer.arg_names = ['value']

    def execute_Integer_cnkeyword(self, symbol):
        return self.execute_Integer(symbol)
    execute_Integer_cnkeyword.arg_names = ['value']

    def execute_String(self, symbol):
        return RuntimeResult().success(String(str(symbol.get('value').value)))
    execute_String.arg_names = ['value']

    def execute_String_cnkeyword(self, symbol):
        return self.execute_String(symbol)
    execute_String_cnkeyword.arg_names = ['value']

    def execute_Float(self, symbol):
        try:
            value = RuntimeResult().success(Float(float(symbol.get('value').value),
                                                  len(str(symbol.get('value').value))))
        except (ValueError, TypeError):
            return RuntimeResult().failure(exception.TypeErrorForFC(
                self.start_pos, self.end_pos,
                f"The argument 'value' can not convert to 'Float'"))
        return value
    execute_Float.arg_names = ['value']

    def execute_Float_cnkeyword(self, symbol):
        return self.execute_Float(symbol)
    execute_Float_cnkeyword.arg_names = ['value']

    def copy(self):
        copy = BuiltinFunction(self.name)
        copy.set_pos(self.start_pos, self.end_pos)
        return copy

    def is_chinese(self):
        return "_cnkeyword" in self.name

    def __repr__(self):
        return f"<Built-in function {self.name}>"


class Array(BaseDataStructure):
    def __init__(self, element_nodes: list[BaseDataStructure]):
        super().__init__(self)
        self.value = element_nodes
        self.start_pos = self.end_pos = None

    def set_pos(self, pos_start: token.Position | None = None, pos_end: token.Position | None = None):
        self.start_pos = pos_start
        self.end_pos = pos_end
        return self

    def sub_block(self, from_, to, step):
        if not isinstance(from_, Integer):
            return None, RuntimeResult().failure(exception.TypeErrorForFC(
                self.start_pos, self.end_pos,
                f"The argument 'from_' must be 'Integer', not '{type(from_).__name__}'"))
        if to is not None and not isinstance(to, Integer):
            return None, RuntimeResult().failure(exception.TypeErrorForFC(
                self.start_pos, self.end_pos,
                f"The argument 'to' must be 'Integer', not '{type(to).__name__}'"))
        if step is not None and not isinstance(step, Integer):
            return None, RuntimeResult().failure(exception.TypeErrorForFC(
                self.start_pos, self.end_pos,
                f"The argument 'step' must be 'Integer', not '{type(step).__name__}'"))
        if hasattr(from_, "value"): from_ = int(from_.value)
        if hasattr(to, "value"): to = int(to.value)
        if to is None: to = from_ + 1
        if hasattr(step, "value"): step = int(step.value)
        if step is None: step = 1
        return self.value[from_:to:step], None

    def add_to(self, other):
        self.value.append(other)
        return Array(self.value), None

    def mul_by(self, other):
        if not isinstance(other, Integer):
            return None, RuntimeResult().failure(exception.TypeErrorForFC(
                self.start_pos, self.end_pos,
                f"The argument 'other' must be 'Integer', not '{type(other).__name__}'"))
        return Array(self.value * int(other.value)), None

    def is_true(self):
        return len(self.value) > 0

    # customize
    def append(self, other):
        self.value.append(other)
        return BaseNullCallBackButValue(None)

    def 添加(self, other):
        self.value.append(other)
        return BaseNullCallBackButValue(None)

    def __repr__(self):
        return f"[{', '.join([str(element) for element in self.value])}]"


class Boolean(BaseDataStructure):
    def __init__(self, value: bool | None):
        super().__init__(self)
        if value is True:
            self.value = "1"
        elif value is False:
            self.value = "0"
        elif value is None:
            self.value = "null"
        self.start_pos = self.end_pos = None

        self.set_pos()

    def set_pos(self, pos_start: token.Position | None = None, pos_end: token.Position | None = None):
        self.start_pos = pos_start
        self.end_pos = pos_end
        return self

    def eq_to(self, other):
        return Boolean(self.value == other.value).set_pos(self.start_pos, other.end_pos), None

    def is_true(self):
        if self.value == "0":
            return False
        else:
            return True

    def __repr__(self):
        if self.value == "1":
            return "true"
        elif self.value == "0":
            return "false"
        else:
            return "null"


class String(BaseDataStructure):
    def __init__(self, value: str):
        super().__init__(self)
        self.value = value
        self.start_pos = self.end_pos = None

        self.set_pos()

    def set_pos(self, pos_start: token.Position | None = None, pos_end: token.Position | None = None):
        self.start_pos = pos_start
        self.end_pos = pos_end
        return self

    def add_to(self, other):
        if not isinstance(other, String):
            return None, RuntimeResult().failure(exception.TypeErrorForFC(
                other.start_pos, other.end_pos,
                f"Unsupported operator '+' for '{type(self).__name__}' and '{type(other).__name__}'"))
        return String(self.value + other.value).set_pos(self.start_pos, other.end_pos), None

    def mul_by(self, other):
        if isinstance(other, Integer):
            return String(self.value * int(other.value)).set_pos(self.start_pos, other.end_pos), None
        return None, RuntimeResult().failure(exception.TypeErrorForFC(
            other.start_pos, other.end_pos,
            f"Unsupported operator '*' for '{type(self).__name__}' and '{type(other).__name__}'"))

    def sub_block(self, from_, to, step):
        if not isinstance(from_, Integer):
            return None, RuntimeResult().failure(exception.TypeErrorForFC(
                self.start_pos, self.end_pos,
                f"The argument 'from_' must be 'Integer', not '{type(from_).__name__}'"))
        if to is not None and not isinstance(to, Integer):
            return None, RuntimeResult().failure(exception.TypeErrorForFC(
                self.start_pos, self.end_pos,
                f"The argument 'to' must be 'Integer', not '{type(to).__name__}'"))
        if step is not None and not isinstance(step, Integer):
            return None, RuntimeResult().failure(exception.TypeErrorForFC(
                self.start_pos, self.end_pos,
                f"The argument 'step' must be 'Integer', not '{type(step).__name__}'"))
        if hasattr(from_, "value"): from_ = int(from_.value)
        if hasattr(to, "value"): to = int(to.value)
        if to is None: to = from_ + 1
        if hasattr(step, "value"): step = int(step.value)
        if step is None: step = 1
        return self.value[from_:to:step], None

    def is_true(self):
        return self.value != ""

    def __repr__(self):
        return f"{self.value}"


class Integer(BaseDataStructure):
    def __init__(self, value: int | str | decimal.Decimal):
        super().__init__(self)
        self.value = str(value)
        self.start_pos = self.end_pos = None

        self.set_pos()

    def set_pos(self, pos_start: token.Position | None = None, pos_end: token.Position | None = None):
        self.start_pos = pos_start
        self.end_pos = pos_end
        return self

    def add_to(self, other) -> tuple:
        if isinstance(other, String):
            return None, RuntimeResult().failure(exception.TypeErrorForFC(
                other.start_pos, other.end_pos,
                f"Unsupported operator '+' for '{type(self).__name__}' and '{type(other).__name__}'"))
        if isinstance(other, Float):
            decimal.getcontext().prec = other.prec
        return Integer(decimal.Decimal(self.value) + decimal.Decimal(other.value)).set_pos(self.start_pos, other.end_pos), None

    def sub_by(self, other) -> tuple:
        if isinstance(other, String):
            return None, RuntimeResult().failure(exception.TypeErrorForFC(
                other.start_pos, other.end_pos,
                f"Unsupported operator '-' for '{type(self).__name__}' and '{type(other).__name__}'"))
        if isinstance(other, Float):
            decimal.getcontext().prec = other.prec
        return Integer(decimal.Decimal(self.value) - decimal.Decimal(other.value)).set_pos(self.start_pos, other.end_pos), None

    def mul_by(self, other) -> tuple:
        if isinstance(other, String):
            return String(int(self.value) * other.value).set_pos(self.start_pos, other.end_pos), None
        if isinstance(other, Float):
            decimal.getcontext().prec = other.prec
        return Integer(decimal.Decimal(self.value) * decimal.Decimal(other.value)).set_pos(self.start_pos, other.end_pos), None

    def div_by(self, other) -> tuple:
        if isinstance(other, String):
            return None, RuntimeResult().failure(exception.TypeErrorForFC(
                other.start_pos, other.end_pos,
                f"Unsupported operator '/' for '{type(self).__name__}' and '{type(other).__name__}'"))
        if decimal.Decimal(other.value) == 0:
            return None, RuntimeResult().failure(exception.ValueErrorForFC(other.start_pos, other.end_pos,
                                                   "Divide by zero (disagreed dividend is 0)"))
        if isinstance(other, Float):
            decimal.getcontext().prec = other.prec
        return Integer(decimal.Decimal(self.value) / decimal.Decimal(other.value)).set_pos(self.start_pos, other.end_pos), None

    def pow_by(self, other) -> tuple:
        if isinstance(other, String):
            return None, RuntimeResult().failure(exception.TypeErrorForFC(
                other.start_pos, other.end_pos,
                f"Unsupported operator '**' for '{type(self).__name__}' and '{type(other).__name__}'"))
        if isinstance(other, Float):
            decimal.getcontext().prec = other.prec
        return Integer(decimal.Decimal(self.value) ** decimal.Decimal(other.value)).set_pos(self.start_pos, other.end_pos), None

    def mod_by(self, other) -> tuple:
        if isinstance(other, String):
            return None, RuntimeResult().failure(exception.TypeErrorForFC(
                other.start_pos, other.end_pos,
                f"Unsupported operator '%' for '{type(self).__name__}' and '{type(other).__name__}'"))
        if decimal.Decimal(other.value) == 0:
            return None, RuntimeResult().failure(exception.ValueErrorForFC(other.start_pos, other.end_pos,
                                                   "Module by zero (disagreed module is 0)"))
        if isinstance(other, Float):
            decimal.getcontext().prec = other.prec
        return Integer(decimal.Decimal(self.value) % decimal.Decimal(other.value)).set_pos(self.start_pos, other.end_pos), None

    def gt_to(self, other):
        if isinstance(other, Float) or isinstance(other, Integer):
            return Boolean(decimal.Decimal(self.value) > decimal.Decimal(other.value)).set_pos(self.start_pos, other.end_pos), None
        else:
            return None, RuntimeResult().failure(exception.TypeErrorForFC(
                other.start_pos, other.end_pos,
                f"Unsupported operator '>' for '{type(self).__name__}' and '{type(other).__name__}'"))

    def lt_to(self, other):
        if isinstance(other, Float) or isinstance(other, Integer):
            return Boolean(decimal.Decimal(self.value) < decimal.Decimal(other.value)).set_pos(self.start_pos, other.end_pos), None
        else:
            return None, RuntimeResult().failure(exception.TypeErrorForFC(
                other.start_pos, other.end_pos,
                f"Unsupported operator '<' for '{type(self).__name__}' and '{type(other).__name__}'"))

    def gte_to(self, other):
        if isinstance(other, Float) or isinstance(other, Integer):
            return Boolean(decimal.Decimal(self.value) >= decimal.Decimal(other.value)).set_pos(self.start_pos, other.end_pos), None
        else:
            return None, RuntimeResult().failure(exception.TypeErrorForFC(
                other.start_pos, other.end_pos,
                f"Unsupported operator '>=' for '{type(self).__name__}' and '{type(other).__name__}'"))

    def lte_to(self, other):
        if isinstance(other, Float) or isinstance(other, Integer):
            return Boolean(decimal.Decimal(self.value) <= decimal.Decimal(other.value)).set_pos(self.start_pos, other.end_pos), None
        else:
            return None, RuntimeResult().failure(exception.TypeErrorForFC(
                other.start_pos, other.end_pos,
                f"Unsupported operator '<=' for '{type(self).__name__}' and '{type(other).__name__}'"))

    def is_true(self):
        if decimal.Decimal(self.value) == decimal.Decimal("0") or decimal.Decimal(self.value) == decimal.Decimal("0.0"):
            return False
        else:
            return True

    def __repr__(self):
        return f"{self.value}"


class Float(BaseDataStructure):
    def __init__(self, value: float | str | decimal.Decimal, prec: int):
        super().__init__(self)
        self.value = str(value)
        self.prec = prec
        self.start_pos = self.end_pos = None

        self.set_pos()

    def set_pos(self, pos_start: token.Position | None = None, pos_end: token.Position | None = None):
        self.start_pos = pos_start
        self.end_pos = pos_end
        return self

    def _calculate_prec(self, other):
        if isinstance(other, Float):
            decimal.getcontext().prec = max(self.prec, other.prec)
        else:
            decimal.getcontext().prec = self.prec

    def add_to(self, other) -> tuple:
        if isinstance(other, String):
            return None, RuntimeResult().failure(exception.TypeErrorForFC(
                other.start_pos, other.end_pos,
                f"Unsupported operator '+' for '{type(self).__name__}' and '{type(other).__name__}'"))
        self._calculate_prec(other)
        return Integer(decimal.Decimal(self.value) + decimal.Decimal(other.value)).set_pos(self.start_pos, other.end_pos), None

    def sub_by(self, other) -> tuple:
        if isinstance(other, String):
            return None, RuntimeResult().failure(exception.TypeErrorForFC(
                other.start_pos, other.end_pos,
                f"Unsupported operator '-' for '{type(self).__name__}' and '{type(other).__name__}'"))
        self._calculate_prec(other)
        return Integer(decimal.Decimal(self.value) - decimal.Decimal(other.value)).set_pos(self.start_pos, other.end_pos), None

    def mul_by(self, other) -> tuple:
        if isinstance(other, String):
            return None, RuntimeResult().failure(exception.TypeErrorForFC(
                other.start_pos, other.end_pos,
                f"Unsupported operator '*' for '{type(self).__name__}' and '{type(other).__name__}'"))
        self._calculate_prec(other)
        return Integer(decimal.Decimal(self.value) * decimal.Decimal(other.value)).set_pos(self.start_pos, other.end_pos), None

    def div_by(self, other) -> tuple:
        if isinstance(other, String):
            return None, RuntimeResult().failure(exception.TypeErrorForFC(
                other.start_pos, other.end_pos,
                f"Unsupported operator '/' for '{type(self).__name__}' and '{type(other).__name__}'"))
        if decimal.Decimal(other.value) == 0:
            return None, RuntimeResult().failure(exception.ValueErrorForFC(other.start_pos, other.end_pos,
                                                   "Divide by zero (disagreed dividend is 0)"))
        self._calculate_prec(other)
        return Integer(decimal.Decimal(self.value) / decimal.Decimal(other.value)).set_pos(self.start_pos, other.end_pos), None

    def pow_by(self, other) -> tuple:
        if isinstance(other, String):
            return None, RuntimeResult().failure(exception.TypeErrorForFC(
                other.start_pos, other.end_pos,
                f"Unsupported operator '**' for '{type(self).__name__}' and '{type(other).__name__}'"))
        self._calculate_prec(other)
        return Integer(decimal.Decimal(self.value) ** decimal.Decimal(other.value)).set_pos(self.start_pos, other.end_pos), None

    def mod_by(self, other) -> tuple:
        if isinstance(other, String):
            return None, RuntimeResult().failure(exception.TypeErrorForFC(
                other.start_pos, other.end_pos,
                f"Unsupported operator '%' for '{type(self).__name__}' and '{type(other).__name__}'"))
        if decimal.Decimal(other.value) == 0:
            return None, RuntimeResult().failure(exception.ValueErrorForFC(other.start_pos, other.end_pos,
                                                   "Module by zero (disagreed module is 0)"))
        self._calculate_prec(other)
        return Integer(decimal.Decimal(self.value) % decimal.Decimal(other.value)).set_pos(self.start_pos, other.end_pos), None

    def gt_to(self, other):
        if isinstance(other, Float) or isinstance(other, Integer):
            return Boolean(decimal.Decimal(self.value) > decimal.Decimal(other.value)).set_pos(self.start_pos, other.end_pos), None
        else:
            return None, RuntimeResult().failure(exception.TypeErrorForFC(
                other.start_pos, other.end_pos,
                f"Unsupported operator '>' for '{type(self).__name__}' and '{type(other).__name__}'"))

    def gte_to(self, other):
        if isinstance(other, Float) or isinstance(other, Integer):
            return Boolean(decimal.Decimal(self.value) >= decimal.Decimal(other.value)).set_pos(self.start_pos, other.end_pos), None
        else:
            return None, RuntimeResult().failure(exception.TypeErrorForFC(
                other.start_pos, other.end_pos,
                f"Unsupported operator '>=' for '{type(self).__name__}' and '{type(other).__name__}'"))

    def lt_to(self, other):
        if isinstance(other, Float) or isinstance(other, Integer):
            return Boolean(decimal.Decimal(self.value) < decimal.Decimal(other.value)).set_pos(self.start_pos, other.end_pos), None
        else:
            return None, RuntimeResult().failure(exception.TypeErrorForFC(
                other.start_pos, other.end_pos,
                f"Unsupported operator '<' for '{type(self).__name__}' and '{type(other).__name__}'"))

    def lte_to(self, other):
        if isinstance(other, Float) or isinstance(other, Integer):
            return Boolean(decimal.Decimal(self.value) <= decimal.Decimal(other.value)).set_pos(self.start_pos, other.end_pos), None
        else:
            return None, RuntimeResult().failure(exception.TypeErrorForFC(
                other.start_pos, other.end_pos,
                f"Unsupported operator '<=' for '{type(self).__name__}' and '{type(other).__name__}'"
            ))

    def is_true(self):
        if decimal.Decimal(self.value) == decimal.Decimal("0") or decimal.Decimal(self.value) == decimal.Decimal("0.0"):
            return False
        else:
            return True

    def __repr__(self):
        return f"{self.value}"


class Interpreter:
    def visit(self, node, symbol: SymbolTable, support_chinese: bool, father_call: BaseDataStructure | None):
        method = getattr(self, f"visit_{type(node).__name__}", self.no_visit_node)
        try:
            return method(node, symbol, support_chinese, father_call)
        except decimal.Overflow:
            return RuntimeResult().failure(exception.OverflowErrorForFC(
                node.pos_start, node.pos_end,
                "Number too large to calculate"))
        except Exception as e:
            return RuntimeResult().failure(exception.ProgramInternalBugErrorForFC(
                node.pos_start, node.pos_end,
                f"Program when interpreting raised an error: \033[1;32;40m{type(e).__name__}: {e}\033[0m\n\n"
                f"\033[35mHere is details\033[0m: \n\033[91m{traceback.format_exc()}\033[0m\n"
                f"\033[35mNoticeWarning\033[0m: "
                f"\033[93mThis error meant that your code might be right, but language you using cores raised an error.\033[0m"))

    def no_visit_node(self, node, *_):
        raise Exception(f"No visit_{type(node).__name__} method include in Interpreter")

    # 语法
    def visit_VarAssignNode(self, node, symbol, support_chinese, father_call):
        res = RuntimeResult()
        evaluated_value = res.register(self.visit(node.var_value_node, symbol, support_chinese, father_call))
        if isinstance(evaluated_value, BaseNullCallBackButValue):
            evaluated_value = evaluated_value.copy_value
        if res.should_return(): return res
        if node.is_reassignment:
            if symbol.get(node.var_name_token.value) is None:
                return res.failure(exception.NameErrorForFC(node.var_name_token.pos_start, node.var_name_token.pos_end,
                                                        f"'{node.var_name_token.value}' is not defined"))
        symbol.set(node.var_name_token.value, evaluated_value)
        return res.success(BaseNullCallBackButValue(evaluated_value))

    @staticmethod
    def visit_VarAccessNode(node, symbol, support_chinese, father_call):
        res = RuntimeResult()

        before_node = node
        if father_call is not None:
            node = father_call

        symbol_value = symbol.get(node.var_name_token.value)
        if symbol_value is None:
            return res.failure(exception.NameErrorForFC(before_node.var_name_token.pos_start, before_node.var_name_token.pos_end,
                                                        f"'{node.var_name_token.value}' is not defined"))
        return res.success(symbol_value)

    def visit_IfNode(self, node, symbol, support_chinese, father_call):
        res = RuntimeResult()

        for condition, expression, should_return_null in node.cases:
            condition_value = res.register(self.visit(condition, symbol, support_chinese, father_call))
            if res.should_return(): return res

            if condition_value.is_true():
                expression_value = res.register(self.visit(expression, symbol, support_chinese, father_call))
                if res.should_return(): return res
                return res.success(Boolean(None) if should_return_null else expression_value)

        if node.else_case:
            expr, should_return_null = node.else_case
            else_value = res.register(self.visit(expr, symbol, support_chinese, father_call))
            if res.should_return(): return res
            return res.success(Boolean(None) if should_return_null else else_value)

        return res.success(BaseNullCallBackButValue(None))

    @staticmethod
    def visit_FunctionDefineNode(node, symbol, support_chinese, father_call):
        res = RuntimeResult()

        func_name = node.var_name_token.value if node.var_name_token else None
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.arg_name_tokens]
        func_value = Function(func_name, body_node, arg_names, support_chinese, father_call
                              ).set_pos(node.pos_start, node.pos_end)

        if node.var_name_token:
            symbol.set(func_name, func_value)

        return res.success(func_value)

    def visit_ClassCallNode(self, node, symbol, support_chinese, father_call):
        res = RuntimeResult()

        father_token_call = node.father_token_call
        result = BaseNullCallBackButValue(None)
        for child_node in node.child_nodes:
            result = res.register(self.visit(child_node, symbol, support_chinese, father_token_call))
            if res.should_return(): return res
            if isinstance(child_node, parser.nodes.FunctionCallNode):
                father_token_call = child_node.node_to_call
            elif isinstance(child_node, parser.nodes.VarAccessNode):
                father_token_call = child_node
            else:
                return res.failure(
                    exception.SyntaxErrorForFC(
                        child_node.pos_start, child_node.pos_end,
                        "Invalid syntax"
                    )
                )

        return res.success(result)

    def visit_FunctionCallNode(self, node, symbol, support_chinese, father_call):
        res = RuntimeResult()
        args = []

        value_to_call = res.register(self.visit(node.node_to_call, symbol, support_chinese, father_call))
        if res.should_return(): return res
        if isinstance(value_to_call, BuiltinFunction):
            if not support_chinese and value_to_call.is_chinese():
                return res.failure(exception.NameErrorForFC(
                    node.node_to_call.pos_start, node.node_to_call.pos_end,
                    f"{node.node_to_call.var_name_token.value} is not defined."))

        if father_call is not None:
            for arg_node in node.arg_nodes:
                args.append(res.register(self.visit(arg_node, symbol, support_chinese, None)))
                if res.should_return(): return res
            if not hasattr(value_to_call, node.node_to_call.var_name_token.value):
                return res.failure(exception.NameErrorForFC(
                    node.node_to_call.pos_start, node.node_to_call.pos_end,
                    f"Method '{node.node_to_call.var_name_token.value}' is not defined."))

            return res.success(getattr(value_to_call, node.node_to_call.var_name_token.value)(*args))

        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)
        for arg_node in node.arg_nodes:
            args.append(res.register(self.visit(arg_node, symbol, support_chinese, father_call)))
            if res.should_return(): return res

        return_value = res.register(value_to_call.execute(args, symbol))
        if res.should_return(): return res

        return_value = return_value.set_pos(node.pos_start, node.pos_end)
        return res.success(return_value)

    def visit_ForNode(self, node, symbol, support_chinese, father_call):
        res = RuntimeResult()

        var_name = node.var_name_token.value
        start_value = res.register(self.visit(node.start_value_node, symbol, support_chinese, father_call))
        if not isinstance(start_value, Integer):
            return res.failure(exception.TypeErrorForFC(
                node.start_value_node.pos_start, node.start_value_node.pos_end,
                f"'{node.start_value_node.value}' is not an integer"))
        if res.should_return(): return res

        end_value = res.register(self.visit(node.end_value_node, symbol, support_chinese, father_call))
        if not isinstance(end_value, Integer):
            return res.failure(exception.TypeErrorForFC(
                node.end_value_node.pos_start, node.end_value_node.pos_end,
                f"'{node.end_value_node.value}' is not an integer"))
        if res.should_return(): return res

        if node.step_value_node:
            step_value = res.register(self.visit(node.step_value_node, symbol, support_chinese, father_call))
            if not isinstance(step_value, Integer):
                return res.failure(exception.TypeErrorForFC(
                    node.step_value_node.pos_start, node.step_value_node.pos_end,
                    f"'{node.step_value_node.value}' is not an integer"))
            if res.should_return(): return res
        else:
            step_value = Integer(1)

        for i in range(int(start_value.value), int(end_value.value) + int(step_value.value),
                       int(step_value.value)):
            symbol.set(var_name, Integer(i))
            res.register(self.visit(node.body_node, symbol, support_chinese, father_call))
            if res.should_return(): return res
            if res.loop_should_continue: continue
            if res.loop_should_break: break

        return res.success(BaseNullCallBackButValue(None))

    def visit_WhileNode(self, node, symbol, support_chinese, father_call):
        res = RuntimeResult()

        while res.register(self.visit(node.condition_node, symbol, support_chinese, father_call)).is_true():
            res.register(self.visit(node.body_node, symbol, support_chinese, father_call))
            if res.should_return(): return res
            if res.loop_should_continue: continue
            if res.loop_should_break: break

        return res.success(BaseNullCallBackButValue(None))

    # 语法糖
    def visit_SubBlockNode(self, node, symbol, support_chinese, father_call):
        res = RuntimeResult()

        value = res.register(self.visit(node.element_nodes, symbol, support_chinese, father_call))
        if res.should_return(): return res

        from_index_token = res.register(self.visit(node.from_index_token, symbol, support_chinese, father_call))
        if res.should_return(): return res
        if node.to_index_token:
            to_index_token = res.register(self.visit(node.to_index_token, symbol, support_chinese, father_call))
            if res.should_return(): return res
        else:
            to_index_token = None
        if node.step_token_token:
            step_token_token = res.register(self.visit(node.step_token_token, symbol, support_chinese, father_call))
            if res.should_return(): return res
        else:
            step_token_token = None

        result, error = value.sub_block(from_index_token, to_index_token, step_token_token)
        if error: return res.failure(error)
        return res.success(result)

    @staticmethod
    def visit_BooleanNode(node, symbol, support_chinese, father_call):
        return RuntimeResult().success(Boolean(node.boolean).set_pos(node.pos_start, node.pos_end))

    @staticmethod
    def visit_StringNode(node, symbol, support_chinese, father_call):
        return RuntimeResult().success(String(node.token.value).set_pos(node.pos_start, node.pos_end))

    @staticmethod
    def visit_IntegerNode(node, symbol, support_chinese, father_call):
        return RuntimeResult().success(Integer(node.token.value).set_pos(node.pos_start, node.pos_end))

    @staticmethod
    def visit_FloatNode(node, symbol, support_chinese, father_call):
        return RuntimeResult().success(Float(node.token.value, node.prec).set_pos(node.pos_start, node.pos_end))

    def visit_ArrayNode(self, node, symbol, support_chinese, father_call):
        res = RuntimeResult()
        elements = []

        for element in node.element_nodes:
            elements.append(res.register(self.visit(element, symbol, support_chinese, father_call)))
            if res.should_return(): return res

        return res.success(Array(elements).set_pos(node.pos_start, node.pos_end))

    def visit_BinaryOperationNode(self, node, symbol, support_chinese, father_call):
        res = RuntimeResult()
        left = res.register(self.visit(node.left_node, symbol, support_chinese, father_call))
        if res.should_return(): return res
        right = res.register(self.visit(node.right_node, symbol, support_chinese, father_call))
        if res.should_return(): return res

        if node.operator_token.type == token.tokens.PLUS:
            result, error = left.add_to(right)
        elif node.operator_token.type == token.tokens.MINUS:
            result, error = left.sub_by(right)
        elif node.operator_token.type == token.tokens.MULTIPLY:
            result, error = left.mul_by(right)
        elif node.operator_token.type == token.tokens.DIVIDE:
            result, error = left.div_by(right)
        elif node.operator_token.type == token.tokens.POW:
            result, error = left.pow_by(right)
        elif node.operator_token.type == token.tokens.MOD:
            result, error = left.mod_by(right)
        elif node.operator_token.type == token.tokens.EQUAL:
            result, error = left.eq_to(right)
        elif node.operator_token.type == token.tokens.NOT_EQUAL:
            result, error = left.ne_to(right)
        elif node.operator_token.type == token.tokens.LESSER:
            result, error = left.lt_to(right)
        elif node.operator_token.type == token.tokens.GREATER:
            result, error = left.gt_to(right)
        elif node.operator_token.type == token.tokens.LESSER_EQUAL:
            result, error = left.lte_to(right)
        elif node.operator_token.type == token.tokens.GREATER_EQUAL:
            result, error = left.gte_to(right)
        else:
            raise Exception(f"No such binary operation '{node.operator_token}'")

        if error:
            return error
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOperationNode(self, node, symbol, support_chinese, father_call):
        res = RuntimeResult()

        if node.operator_token.type == token.tokens.MINUS:
            number = res.register(self.visit(node.node, symbol, support_chinese, father_call))
            if res.should_return(): return res
            number, error = number.mul_by(Integer(-1))
        elif node.operator_token.type == token.tokens.NOT:
            number = res.register(self.visit(node.node, symbol, support_chinese, father_call))
            if res.should_return(): return res
            number, error = number.eq_to(Boolean(False))
        else:
            number = res.register(self.visit(node.node, symbol, support_chinese, father_call))
            if res.should_return(): return res
            number, error = number.mul_by(Integer(1))

        if error:
            return error
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))

    @staticmethod
    def visit_BreakNode(node, symbol, support_chinese, father_call):
        return RuntimeResult().success_break()

    @staticmethod
    def visit_ContinueNode(node, symbol, support_chinese, father_call):
        return RuntimeResult().success_continue()

    def visit_ReturnNode(self, node, symbol, support_chinese, father_call):
        res = RuntimeResult()
        if node.node_to_return:
            value = res.register(self.visit(node.node_to_return, symbol, support_chinese, father_call))
            if res.should_return(): return res
        else:
            value = Boolean(None)

        return res.success_return(value)

    def visit_ExecutableNode(self, node, symbol, support_chinese, father_call):
        res = RuntimeResult()

        result = []

        for element in node.element_nodes:
            result.append(res.register(self.visit(element, symbol, support_chinese, father_call)))
            if res.should_return(): return res

        return res.success(result[0] if len(result) == 1 else result)


# 内置函数
BuiltinFunction.output = BuiltinFunction("output")
BuiltinFunction.readline = BuiltinFunction("readline")
BuiltinFunction.readline_cnkeyword =BuiltinFunction("readline_cnkeyword")
BuiltinFunction.output_cnkeyword = BuiltinFunction("output_cnkeyword")
BuiltinFunction.run = BuiltinFunction("run")
BuiltinFunction.run_cnkeyword = BuiltinFunction("run_cnkeyword")
BuiltinFunction.Integer = BuiltinFunction("Integer")
BuiltinFunction.Integer_cnkeyword = BuiltinFunction("Integer_cnkeyword")
BuiltinFunction.Float = BuiltinFunction("Float")
BuiltinFunction.Float_cnkeyword = BuiltinFunction("Float_cnkeyword")
BuiltinFunction.String = BuiltinFunction("String")
BuiltinFunction.String_cnkeyword = BuiltinFunction("String_cnkeyword")

SymbolTable_ = SymbolTable()
SymbolTable_.set("output", BuiltinFunction.output)
SymbolTable_.set("输出", BuiltinFunction.output_cnkeyword)
SymbolTable_.set("readline", BuiltinFunction.readline)
SymbolTable_.set("输入", BuiltinFunction.readline_cnkeyword)
SymbolTable_.set("run", BuiltinFunction.run)
SymbolTable_.set("运行", BuiltinFunction.run_cnkeyword)
SymbolTable_.set("Integer", BuiltinFunction.Integer)
SymbolTable_.set("整数", BuiltinFunction.Integer_cnkeyword)
SymbolTable_.set("Float", BuiltinFunction.Float)
SymbolTable_.set("小数", BuiltinFunction.Float_cnkeyword)
SymbolTable_.set("String", BuiltinFunction.String)
SymbolTable_.set("文本", BuiltinFunction.String_cnkeyword)


def run(syntax_: str, support_chinese_keyword: bool,
              quote_file: str, quote_module: str, symbol=SymbolTable_
        ) -> RuntimeResult | exception.BaseExceptionForFC:
    error, tokens = token.Lexer(syntax_, support_chinese_keyword, quote_file, quote_module).make_token()

    if len(tokens) == 1: return RuntimeResult().success(BaseNullCallBackButValue(None))
    if error: return error

    parser_ = parser.Parser(tokens)
    ast = parser_.parse()
    if ast.error: return ast.error

    interpreter = Interpreter().visit(ast.node, symbol, support_chinese_keyword, None)
    if interpreter.error: return interpreter.error

    return interpreter
