from .nodes import ExecutableNode
from .. import token
from .. import exception
from . import nodes


class ParserResult:
    def __init__(self, error=None, node=None):
        self.error = error
        self.node = node
        self.advance_count = 0
        self.to_reverse_count = 0

    def try_register(self, res):
        if res.error:
            self.to_reverse_count = res.advance_count
            return None
        return self.register(res)

    def register(self, res):
        if isinstance(res, ParserResult):
            if res.error:
                self.error = res.error
            return res.node
        elif isinstance(res, token.Token):
            self.advance_count += 1
        return res

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self


class Parser:
    def __init__(self, tokens_: list[token.Token]):
        self.tokens = tokens_

        self.token_index = -1
        self.current_token: token.Token | None = None

        self.advance()

    def parse(self) -> ParserResult:
        res = self.statements()

        if not res.error and self.current_token.type != token.tokens.EOF:
            return res.failure(exception.SyntaxErrorForFC(
                self.current_token.pos_start, self.current_token.pos_end,
                "Token cannot appear after previous tokens"
            ))
        return res

    def advance(self):
        self.token_index += 1
        self._update_current_tok()
        return self.current_token

    def reverse(self, amount=1):
        self.token_index -= amount
        self._update_current_tok()
        return self.token_index

    def _update_current_tok(self):
        if 0 <= self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]

    def while_expression(self):
        res = ParserResult()

        if self.current_token.type != token.tokens.LEFT_PARENT:
            return res.failure(exception.SyntaxErrorForFC(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '('"
            ))

        res.register(self.advance())

        condition = res.register(self.condition())
        if res.error: return res

        if self.current_token.type != token.tokens.RIGHT_PARENT:
            return res.failure(exception.SyntaxErrorForFC(
                self.current_token.pos_start, self.current_token.pos_end,
                "Parentheses are not closed, did you forget ')'?"
            ))

        res.register(self.advance())

        if self.current_token.type != token.tokens.LEFT_FLAG:
            return res.failure(exception.SyntaxErrorForFC(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '{'"
            ))

        res.register(self.advance())

        if self.current_token.type == token.tokens.NEWLINE:
            res.register(self.advance())

            body = res.register(self.statements())
            if res.error: return res

            if self.current_token.type != token.tokens.RIGHT_FLAG:
                return res.failure(exception.SyntaxErrorForFC(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Codes are not closed, did you forget '}'?"
                ))
            res.register(self.advance())

            return res.success(nodes.WhileNode(condition, body))

        body = res.register(self.statement())
        if res.error: return res
        res.register(self.advance())

        return res.success(nodes.WhileNode(condition, body))

    def for_expression(self):
        res = ParserResult()

        if self.current_token.type != token.tokens.VARIABLE:
            return res.failure(exception.SyntaxErrorForFC(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected identifier"
            ))

        var_name = self.current_token
        res.register(self.advance())

        if not self.current_token.matches(token.tokens.KEYWORD, token.tokens.KWLIST_EN[8]) and not \
                self.current_token.matches(token.tokens.KEYWORD, token.tokens.KWLIST_ZH[8]):
            return res.failure(exception.SyntaxErrorForFC(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected 'from'"
            ))

        res.register(self.advance())

        from_value = res.register(self.condition())
        if res.error: return res

        if not self.current_token.matches(token.tokens.KEYWORD, token.tokens.KWLIST_EN[9]) and not \
                self.current_token.matches(token.tokens.KEYWORD, token.tokens.KWLIST_ZH[9]):
            return res.failure(exception.SyntaxErrorForFC(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected 'to'"
            ))

        res.register(self.advance())

        to_value = res.register(self.condition())
        if res.error: return res

        step_value = None
        if self.current_token.matches(token.tokens.KEYWORD, token.tokens.KWLIST_EN[10]) or \
                self.current_token.matches(token.tokens.KEYWORD, token.tokens.KWLIST_ZH[10]):
            res.register(self.advance())
            step_value = res.register(self.condition())
            if res.error: return res

        if self.current_token.type != token.tokens.LEFT_FLAG:
            return res.failure(exception.SyntaxErrorForFC(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '{'"
            ))

        res.register(self.advance())

        if self.current_token.type == token.tokens.NEWLINE:
            res.register(self.advance())

            body = res.register(self.statements())
            if res.error: return res

            if self.current_token.type != token.tokens.RIGHT_FLAG:
                return res.failure(exception.SyntaxErrorForFC(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Codes are not closed, did you forget '}'?"
                ))

            res.register(self.advance())

            return res.success(nodes.ForNode(var_name, from_value, to_value, body, step_value))

        body_nodes = res.register(self.statement())
        if res.error: return res

        res.register(self.advance())

        return res.success(nodes.ForNode(var_name, from_value, to_value, body_nodes, step_value, False))

    def function_expression(self):
        res = ParserResult()

        if self.current_token.type != token.tokens.VARIABLE:
            return res.failure(exception.SyntaxErrorForFC(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected identifier or function name"
            ))
        var_name = self.current_token

        res.register(self.advance())
        if self.current_token.type != token.tokens.LEFT_PARENT:
            return res.failure(exception.SyntaxErrorForFC(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '('"
            ))

        res.register(self.advance())
        arg_name_tokens = []

        if self.current_token.type == token.tokens.VARIABLE:
            arg_name_tokens.append(self.current_token)
            res.register(self.advance())

            while self.current_token.type == token.tokens.COMMA:
                res.register(self.advance())

                if self.current_token.type != token.tokens.VARIABLE:
                    return res.failure(exception.SyntaxErrorForFC(
                        self.current_token.pos_start, self.current_token.pos_end,
                        f"Expected identifier"
                    ))

                arg_name_tokens.append(self.current_token)
                res.register(self.advance())

            if self.current_token.type != token.tokens.RIGHT_PARENT:
                return res.failure(exception.SyntaxErrorForFC(
                    self.current_token.pos_start, self.current_token.pos_end,
                    f"Expected ',' or ')'"
                ))
        else:
            if self.current_token.type != token.tokens.RIGHT_PARENT:
                return res.failure(exception.SyntaxErrorForFC(
                    self.current_token.pos_start, self.current_token.pos_end,
                    f"Expected identifier or ')'"
                ))

        res.register(self.advance())

        if self.current_token.type != token.tokens.LEFT_FLAG:
            return res.failure(exception.SyntaxErrorForFC(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '{'"
            ))

        res.register(self.advance())
        body_node = res.register(self.statements())

        if self.current_token.type != token.tokens.RIGHT_FLAG:
            return res.failure(exception.SyntaxErrorForFC(
                self.current_token.pos_start, self.current_token.pos_end,
                "Codes are not closed, did you forget '}'"
            ))
        res.register(self.advance())
        if res.error: return res
        return res.success(nodes.FunctionDefineNode(var_name, arg_name_tokens, body_node))

    def if_expression(self):
        res = ParserResult()
        all_cases = res.register(self.if_expression_cases(token.tokens.KWLIST_EN[4]))
        if res.error: return res
        cases, else_case = all_cases
        return res.success(nodes.IfNode(cases, else_case))

    def if_expression_b(self):
        return self.if_expression_cases(f'{token.tokens.KWLIST_EN[5]} {token.tokens.KWLIST_EN[4]}|'
                                        f'{token.tokens.KWLIST_ZH[5]} {token.tokens.KWLIST_EN[4]}')

    def if_expression_c(self):
        res = ParserResult()
        else_case = None

        if self.current_token.type == token.tokens.LEFT_FLAG:
            res.register(self.advance())

            if self.current_token.type == token.tokens.NEWLINE:
                res.register(self.advance())

                statements = res.register(self.statements())
                if res.error: return res
                else_case = (statements, True)

                if self.current_token.type == token.tokens.RIGHT_FLAG:
                    res.register(self.advance())
                else:
                    return res.failure(exception.SyntaxErrorForFC(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "Codes are not closed, did you forget '}'?"
                    ))
            else:
                expr = res.register(self.statement())
                if res.error: return res
                else_case = (expr, False)
                # res.register(self.advance())

        return res.success(else_case)

    def if_expression_b_or_c(self):
        res = ParserResult()
        cases, else_case = [], None

        if self.current_token.matches(token.tokens.KEYWORD, token.tokens.KWLIST_EN[5]) or \
                self.current_token.matches(token.tokens.KEYWORD, token.tokens.KWLIST_ZH[5]):
            res.register(self.advance())
            if self.current_token.matches(token.tokens.KEYWORD, token.tokens.KWLIST_EN[4]) or \
                    self.current_token.matches(token.tokens.KEYWORD, token.tokens.KWLIST_ZH[4]):
                self.reverse()
                all_cases = res.register(self.if_expression_b())
                if res.error: return res
                cases, else_case = all_cases
            else:
                else_case = res.register(self.if_expression_c())
                if res.error: return res
        else:
            else_case = res.register(self.if_expression_c())
            if res.error: return res

        return res.success((cases, else_case))

    def if_expression_cases(self, case_keyword):
        res = ParserResult()
        cases = []
        case_keyword = case_keyword.split("|")

        check = False
        for case_word in case_keyword:
            case_word = case_word.split()
            for word in case_word:
                if not self.current_token.matches(token.tokens.KEYWORD, word):
                    check = exception.SyntaxErrorForFC(
                        self.current_token.pos_start, self.current_token.pos_end,
                        f"Expected '{case_word}'"
                    )
                else:
                    check = True

                res.register(self.advance())
        if isinstance(check, str):
            return res.failure(check)

        condition = res.register(self.condition())
        if res.error: return res
        if self.current_token.type != token.tokens.LEFT_FLAG:
            return res.failure(exception.SyntaxErrorForFC(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '{'"
            ))

        res.register(self.advance())

        if self.current_token.type == token.tokens.NEWLINE:
            res.register(self.advance())

            statements = res.register(self.statements())
            if res.error: return res
            cases.append((condition, statements, True))

            if self.current_token.type == token.tokens.RIGHT_FLAG:
                res.register(self.advance())
            all_cases = res.register(self.if_expression_b_or_c())
            if res.error: return res
            new_cases, else_case = all_cases
            cases.extend(new_cases)
        else:
            expr = res.register(self.statement())
            if res.error: return res
            cases.append((condition, expr, False))

            if self.current_token.type == token.tokens.RIGHT_FLAG:
                res.register(self.advance())
            else:
                return res.failure(exception.SyntaxErrorForFC(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Codes are not closed, did you forget '}'?"
                ))

            all_cases = res.register(self.if_expression_b_or_c())
            if res.error: return res
            new_cases, else_case = all_cases
            cases.extend(new_cases)

        return res.success((cases, else_case))

    def list_expression(self):
        res = ParserResult()
        elements = []

        while self.current_token.type not in (token.tokens.COMMA, token.tokens.RIGHT_BRACKET):
            element = res.register(self.statements())
            if res.error: return res
            elements.append(element)
            if self.current_token.type == token.tokens.RIGHT_BRACKET:
                break
            elif self.current_token.type == token.tokens.EOF:
                return res.failure(exception.SyntaxErrorForFC(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "List expression is not closed, did you forget ']'?"
                ))
            res.register(self.advance())

        res.register(self.advance())
        if self.current_token.type == token.tokens.LEFT_BRACKET:
            res.register(self.advance())
            index = []
            while self.current_token.type != token.tokens.ONION:
                current_index = res.register(self.condition())
                if res.error: return res
                index.append(current_index)
                if self.current_token.type == token.tokens.RIGHT_BRACKET:
                    res.register(self.advance())
                    break
                elif self.current_token.type == token.tokens.EOF:
                    return res.failure(exception.SyntaxErrorForFC(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "List expression is not closed, did you forget ']'?"
                    ))

                res.register(self.advance())
            return res.success(nodes.SubBlockNode(nodes.ArrayNode(elements), *index))

        return res.success(nodes.ArrayNode(elements))

    def atom(self, linking_call: bool = True):
        res = ParserResult()
        tok = self.current_token
        # 一元计算
        if tok.type in (token.tokens.PLUS, token.tokens.MINUS):
            res.register(self.advance())
            atom = res.register(self.atom())
            if res.error: return res
            return res.success(nodes.UnaryOperationNode(tok, atom))

        elif tok.type == token.tokens.NOT:
            res.register(self.advance())
            if self.current_token.type == token.tokens.LEFT_PARENT:
                res.register(self.advance())
                condition = res.register(self.condition())
                if res.error: return res
                if self.current_token.type == token.tokens.RIGHT_PARENT:
                    res.register(self.advance())
                else:
                    return res.failure(exception.SyntaxErrorForFC(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "Parenthesis is not closed, did you forget ')'?"
                    ))
                return res.success(nodes.UnaryOperationNode(tok, condition))
            else:
                return res.failure(exception.SyntaxErrorForFC(tok.pos_start, self.current_token.pos_end,
                                                            "Expected '('"))

        elif tok.type == token.tokens.VARIABLE:
            res.register(self.advance())
            if self.current_token.type == token.tokens.COPY:
                res.register(self.advance())
                expr = res.register(self.condition())
                if res.error: return res
                return res.success(nodes.VarAssignNode(tok, expr, True))
            elif self.current_token.type == token.tokens.LEFT_PARENT:
                res.register(self.advance())
                function_calling = tok
                arg_values = []

                while self.current_token.type not in (token.tokens.RIGHT_PARENT, token.tokens.RIGHT_FLAG):
                    condition = res.register(self.condition())
                    if res.error: return res
                    arg_values.append(condition)
                    if self.current_token.type == token.tokens.COMMA:
                        res.register(self.advance())

                if self.current_token.type != token.tokens.RIGHT_PARENT:
                    return res.failure(exception.SyntaxErrorForFC(tok.pos_start, self.current_token.pos_end,
                                                                  "Parenthesis is not closed, did you forget ')'?"))
                res.register(self.advance())
                return res.success(nodes.FunctionCallNode(nodes.VarAccessNode(function_calling), arg_values))
            elif self.current_token.type == token.tokens.DOT and linking_call:
                res.register(self.advance())

                atom = []
                while self.current_token.type == token.tokens.VARIABLE:
                    atom.append(res.register(self.atom(False)))
                    if res.error: return res

                    res.register(self.advance())

                return res.success(nodes.ClassCallNode(nodes.VarAccessNode(tok), atom))
            return res.success(nodes.VarAccessNode(tok))

        # 语法
        elif tok.matches(token.tokens.KEYWORD, token.tokens.KWLIST_EN[0]) or \
                tok.matches(token.tokens.KEYWORD, token.tokens.KWLIST_ZH[0]):
            res.register(self.advance())
            if self.current_token.type == token.tokens.VARIABLE:
                var_name = self.current_token
                res.register(self.advance())
                if self.current_token.type == token.tokens.COPY:
                    res.register(self.advance())
                    expr = res.register(self.condition())
                    if res.error: return res
                    return res.success(nodes.VarAssignNode(var_name, expr))
                else:
                    return res.failure(exception.SyntaxErrorForFC(tok.pos_start, self.current_token.pos_end,
                                                                  "Expected '='"))
            else:
                return res.failure(exception.SyntaxErrorForFC(tok.pos_start, self.current_token.pos_end,
                                                              "Expected any identifier, but other"))

        elif tok.matches(token.tokens.KEYWORD, token.tokens.KWLIST_EN[1]) or \
                tok.matches(token.tokens.KEYWORD, token.tokens.KWLIST_ZH[1]):
            res.register(self.advance())
            return res.success(nodes.BooleanNode(tok, True))

        elif tok.matches(token.tokens.KEYWORD, token.tokens.KWLIST_EN[2]) or \
                tok.matches(token.tokens.KEYWORD, token.tokens.KWLIST_ZH[2]):
            res.register(self.advance())
            return res.success(nodes.BooleanNode(tok, False))

        elif tok.matches(token.tokens.KEYWORD, token.tokens.KWLIST_EN[3]) or \
                tok.matches(token.tokens.KEYWORD, token.tokens.KWLIST_ZH[3]):
            res.register(self.advance())
            return res.success(nodes.BooleanNode(tok, None))

        elif tok.matches(token.tokens.KEYWORD, token.tokens.KWLIST_EN[4]) or \
                tok.matches(token.tokens.KEYWORD, token.tokens.KWLIST_ZH[4]):
            if_expression = res.register(self.if_expression())
            if res.error: return res
            return res.success(if_expression)

        elif tok.matches(token.tokens.KEYWORD, token.tokens.KWLIST_EN[6]) or \
                tok.matches(token.tokens.KEYWORD, token.tokens.KWLIST_ZH[6]):
            res.register(self.advance())
            function_expression = res.register(self.function_expression())
            if res.error: return res
            return res.success(function_expression)

        elif tok.matches(token.tokens.KEYWORD, token.tokens.KWLIST_EN[7]) or \
                tok.matches(token.tokens.KEYWORD, token.tokens.KWLIST_ZH[7]):
            res.register(self.advance())
            for_expression = res.register(self.for_expression())
            if res.error: return res
            return res.success(for_expression)

        elif tok.matches(token.tokens.KEYWORD, token.tokens.KWLIST_EN[11]) or \
                tok.matches(token.tokens.KEYWORD, token.tokens.KWLIST_ZH[11]):
            res.register(self.advance())
            while_expression = res.register(self.while_expression())
            if res.error: return res
            return res.success(while_expression)

        # 数据结构
        elif tok.type == token.tokens.INT:
            res.register(self.advance())
            return res.success(nodes.IntegerNode(tok))

        elif tok.type == token.tokens.FLOAT:
            res.register(self.advance())
            return res.success(nodes.FloatNode(tok, tok.addition))

        elif tok.type == token.tokens.STRING:
            res.register(self.advance())
            return res.success(nodes.StringNode(tok))

        # 括号展开
        elif tok.type == token.tokens.LEFT_PARENT:
            res.register(self.advance())
            expr = res.register(self.condition())
            if res.error: return res
            if self.current_token.type == token.tokens.RIGHT_PARENT:
                res.register(self.advance())
                return res.success(expr)
            else:
                return res.failure(exception.SyntaxErrorForFC(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Parenthesis is not closed, did you forget ')'?"
                ))

        elif tok.type == token.tokens.LEFT_BRACKET:
            res.register(self.advance())
            list_expr = res.register(self.list_expression())
            if res.error: return res
            return res.success(list_expr)

        return res.failure(exception.SyntaxErrorForFC(self.current_token.pos_start, self.current_token.pos_end,
                                                    "Expected type 'Integer' or 'Float'"))

    def factor(self):
        return self.binary_operation(self.atom, [token.tokens.POW, token.tokens.MOD])

    def term(self):
        return self.binary_operation(self.factor, [token.tokens.MULTIPLY, token.tokens.DIVIDE])

    def expression(self):
        return self.binary_operation(self.term, [token.tokens.PLUS, token.tokens.MINUS])

    def condition(self):
        return self.binary_operation(self.expression, [token.tokens.EQUAL, token.tokens.NOT_EQUAL,
                                                      token.tokens.GREATER, token.tokens.GREATER_EQUAL,
                                                      token.tokens.LESSER, token.tokens.LESSER_EQUAL])

    def statements(self):
        res = ParserResult()
        statements = []
        pos_start = self.current_token.pos_start.copy()

        while self.current_token.type == token.tokens.NEWLINE:
            res.register(self.advance())

        statement = res.register(self.statement())
        if res.error: return res
        statements.append(statement)

        more_statements = True

        while True:
            newline_count = 0
            while self.current_token.type == token.tokens.NEWLINE:
                res.register(self.advance())
                newline_count += 1
            if newline_count == 0:
                more_statements = False

            if not more_statements: break
            statement = res.try_register(self.statement())
            if not statement:
                self.reverse(res.to_reverse_count)
                more_statements = False
                continue
            statements.append(statement)
        return res.success(ExecutableNode(
            statements,
            pos_start,
            self.current_token.pos_end.copy()
        ))

    def statement(self):
        res = ParserResult()
        pos_start = self.current_token.pos_start.copy()
        if self.current_token.matches(token.tokens.KEYWORD, token.tokens.KWLIST_EN[14]) or \
                self.current_token.matches(token.tokens.KEYWORD, token.tokens.KWLIST_ZH[14]):
            res.register(self.advance())

            expr = res.try_register(self.condition())
            if not expr:
                self.reverse(res.to_reverse_count)
            return res.success(nodes.ReturnNode(expr, pos_start, self.current_token.pos_start.copy()))

        if self.current_token.matches(token.tokens.KEYWORD, token.tokens.KWLIST_EN[13]) or \
                self.current_token.matches(token.tokens.KEYWORD, token.tokens.KWLIST_ZH[13]):
            res.register(self.advance())
            return res.success(nodes.ContinueNode(pos_start, self.current_token.pos_start.copy()))

        if self.current_token.matches(token.tokens.KEYWORD, token.tokens.KWLIST_EN[12]) or \
                self.current_token.matches(token.tokens.KEYWORD, token.tokens.KWLIST_ZH[12]):
            res.register(self.advance())
            return res.success(nodes.BreakNode(pos_start, self.current_token.pos_start.copy()))

        expr = res.register(self.condition())
        if res.error:
            return res.failure(exception.SyntaxErrorForFC(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected 'Integer' , 'Float' or 'String'"
            ))
        return res.success(expr)

    def binary_operation(self, function: callable, operators: list):
        res = ParserResult()
        left = res.register(function())
        if res.error: return res

        while self.current_token.type in operators:
            operator_token = self.current_token
            res.register(self.advance())
            right = res.register(function())
            if res.error: return res
            left = nodes.BinaryOperationNode(left, operator_token, right)

        return res.success(left)
