class ExecutableNode:
    def __init__(self, element_nodes: list, pos_start, pos_end):
        self.element_nodes = element_nodes

        self.pos_start = pos_start
        self.pos_end = pos_end


# 语法
class VarAssignNode:
    def __init__(self, var_name_token, var_value_node, is_reassignment: bool = False):
        self.var_name_token = var_name_token
        self.var_value_node = var_value_node
        self.is_reassignment = is_reassignment

        self.pos_start = self.var_name_token.pos_start
        self.pos_end = self.var_value_node.pos_end

    def __repr__(self):
        return f'{self.var_name_token} = {self.var_value_node}'


class VarAccessNode:
    def __init__(self, var_name_token):
        self.var_name_token = var_name_token

        self.pos_start = self.var_name_token.pos_start
        self.pos_end = self.var_name_token.pos_end

    def __repr__(self):
        return f'{self.var_name_token} = <???>'


class IfNode:
    def __init__(self, cases, else_case):
        self.cases = cases
        self.else_case = else_case

        self.pos_start = self.cases[0][0].pos_start
        self.pos_end = (self.else_case or self.cases[len(self.cases) - 1])[0].pos_end


class FunctionDefineNode:
    def __init__(self, var_name_token, arg_name_tokens, body_node):
        self.var_name_token = var_name_token
        self.arg_name_tokens = arg_name_tokens
        self.body_node = body_node

        self.pos_start = self.var_name_token.pos_start
        self.pos_end = self.body_node.pos_end


class FunctionCallNode:
    def __init__(self, node_to_call, arg_nodes):
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes

        self.pos_start = self.node_to_call.pos_start
        if self.arg_nodes:
            self.pos_end = (self.arg_nodes[len(self.arg_nodes) - 1] or self.node_to_call).pos_end
        else:
            self.pos_end = self.node_to_call.pos_end


class ClassCallNode:
    def __init__(self, father_token_call, child_nodes):
        self.father_token_call = father_token_call
        self.child_nodes = child_nodes

        self.pos_start = self.father_token_call.pos_start
        self.pos_end = self.child_nodes[-1].pos_end


class ForNode:
    def __init__(self, var_name_token, start_value_node, end_value_node, body_node, step_value_node=None):
        self.var_name_token = var_name_token
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node

        self.pos_start = self.var_name_token.pos_start
        self.pos_end = self.body_node.pos_end


class WhileNode:
    def __init__(self, condition_node, body_node):
        self.condition_node = condition_node
        self.body_node = body_node

        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end


class BreakNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end


class ContinueNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end


class ReturnNode:
    def __init__(self, node_to_return, pos_start, pos_end):
        self.node_to_return = node_to_return

        self.pos_start = pos_start
        self.pos_end = pos_end


class BooleanNode:
    def __init__(self, token, boolean):
        self.token = token
        self.boolean = boolean

        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end

    def __repr__(self):
        return f'{self.token}'


class StringNode:
    def __init__(self, token):
        self.token = token

        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end

    def __repr__(self):
        return f'{self.token}'


class IntegerNode:
    def __init__(self, token):
        self.token = token

        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end

    def __repr__(self):
        return f'{self.token}'


class SubBlockNode:
    def __init__(self, element_nodes, from_index_token, to_index_token=None, step_token_token=None):
        self.element_nodes = element_nodes
        self.from_index_token = from_index_token
        self.to_index_token = to_index_token
        self.step_token_token = step_token_token

        self.pos_start = self.from_index_token.pos_start
        if self.to_index_token:
            self.pos_end = self.to_index_token.pos_end
        elif self.step_token_token:
            self.pos_end = self.step_token_token.pos_end
        else:
            self.pos_end = self.from_index_token.pos_end


class ArrayNode:
    def __init__(self, element_nodes):
        self.element_nodes = element_nodes

        if len(self.element_nodes) > 0:
            self.pos_start = self.element_nodes[0].pos_start
            self.pos_end = self.element_nodes[len(self.element_nodes) - 1].pos_end
        else:
            self.pos_start = self.pos_end = None


class FloatNode:
    def __init__(self, token, prec):
        self.token = token
        self.prec = prec

        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end

    def __repr__(self):
        return f'{self.token}'


class BinaryOperationNode:
    def __init__(self, left_node, operator_token, right_node):
        self.left_node = left_node
        self.operator_token = operator_token
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.operator_token}, {self.right_node})'


class UnaryOperationNode:
    def __init__(self, operator_token, node):
        self.operator_token = operator_token
        self.node = node

        self.pos_start = self.operator_token.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        return f'({self.operator_token}, {self.node})'
