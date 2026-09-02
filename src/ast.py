class ASTNode:
    def __init__(self, line: int = 0, col: int = 0):
        self.line = line
        self.col = col


class ProgramNode(ASTNode):
    def __init__(self, statements, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.statements = statements

    def __repr__(self):
        return f"Program({self.statements})"


class LetNode(ASTNode):
    def __init__(self, name, value, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.name = name
        self.value = value

    def __repr__(self):
        return f"Let({self.name}, {self.value})"


class AssignNode(ASTNode):
    def __init__(self, target, op, value, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.target = target
        self.op = op
        self.value = value

    def __repr__(self):
        return f"Assign({self.target}, {self.op}, {self.value})"


class OutputNode(ASTNode):
    def __init__(self, values, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.values = values

    def __repr__(self):
        return f"Output({self.values})"


class ReturnNode(ASTNode):
    def __init__(self, value, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.value = value

    def __repr__(self):
        return f"Return({self.value})"


class BlockNode(ASTNode):
    def __init__(self, statements, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.statements = statements

    def __repr__(self):
        return f"Block({self.statements})"


class IfNode(ASTNode):
    def __init__(self, condition, body, elifs=None, else_body=None, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.condition = condition
        self.body = body
        self.elifs = elifs or []
        self.else_body = else_body

    def __repr__(self):
        return f"If({self.condition}, {self.body}, elifs={self.elifs}, else={self.else_body})"


class WhileNode(ASTNode):
    def __init__(self, condition, body, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"While({self.condition}, {self.body})"


class ForNode(ASTNode):
    def __init__(self, name, iterable, body, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.name = name
        self.iterable = iterable
        self.body = body

    def __repr__(self):
        return f"For({self.name}, {self.iterable}, {self.body})"


class FunctionNode(ASTNode):
    def __init__(self, name, params, body, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.name = name
        self.params = params
        self.body = body

    def __repr__(self):
        return f"Function({self.name}, params={self.params}, body={self.body})"


class ExprStatementNode(ASTNode):
    def __init__(self, expr, line: int, col: int):
        super().__init__(line, col)
        self.expr = expr

    def __repr__(self):
        return f"ExprStmt({self.expr})"


class NumberNode(ASTNode):
    def __init__(self, value, line: int, col: int):
        super().__init__(line, col)
        self.value = value

    def __repr__(self):
        return f"Number({self.value})"


class StringNode(ASTNode):
    def __init__(self, value, line: int, col: int):
        super().__init__(line, col)
        self.value = value

    def __repr__(self):
        return f"String({self.value})"


class IdentifierNode(ASTNode):
    def __init__(self, value, line: int, col: int):
        super().__init__(line, col)
        self.value = value

    def __repr__(self):
        return f"Identifier({self.value})"


class CallNode(ASTNode):
    def __init__(self, callee, args, line: int, col: int):
        super().__init__(line, col)
        self.callee = callee
        self.args = args

    def __repr__(self):
        return f"Call({self.callee}, {self.args})"


class BinaryOpNode(ASTNode):
    def __init__(self, left, op, right, line: int, col: int):
        super().__init__(line, col)
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f"BinOp({self.left}, {self.op}, {self.right})"


class UnaryOpNode(ASTNode):
    def __init__(self, op, right, line: int, col: int):
        super().__init__(line, col)
        self.op = op
        self.right = right

    def __repr__(self):
        return f"UnaryOp({self.op}, {self.right})"

class BooleanNode(ASTNode):
    def __init__(self, value, line: int, col: int):
        super().__init__(line, col)
        self.value = value

    def __repr__(self):
        return f"Boolean({self.value})"

class NullNode(ASTNode):
    def __init__(self, line: int, col: int):
        super().__init__(line, col)

    def __repr__(self):
        return "Null()"
    