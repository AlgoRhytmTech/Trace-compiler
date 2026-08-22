from builtins import len

from .ast import *


class RuntimeError(Exception):
    pass


class Return(Exception):
    def __init__(self, value):
        self.value = value


class Environment:
    def __init__(self, parent=None):
        self.parent = parent
        self.values = {}

    def define(self, name, value):
        self.values[name] = value

    def get(self, name):
        if name in self.values:
            return self.values[name]
        if self.parent is not None:
            return self.parent.get(name)
        raise RuntimeError(f"Undefined name '{name}'")

    def set(self, name, value):
        if name in self.values:
            self.values[name] = value
            return
        if self.parent is not None:
            self.parent.set(name, value)
            return
        raise RuntimeError(f"Undefined name '{name}'")


class UserFunction:
    def __init__(self, declaration, closure):
        self.declaration = declaration
        self.closure = closure

    def call(self, interpreter, args):
        params = self.declaration.params
        if len(args) != len(params):
            raise RuntimeError(
                f"Function {self.declaration.name} expects {len(params)} arguments"
            )

        env = Environment(self.closure)
        for param, arg in zip(params, args):
            env.define(param, arg)

        try:
            interpreter.execute_block(self.declaration.body.statements, env)
        except Return as ret:
            return ret.value
        return None


class Interpreter:
    def __init__(self):
        self.globals = Environment()
        self.globals.define("input", input)
        self.globals.define("range",range)
        self.globals.define("len",len)
        

        self.env = self.globals

    def interpret(self, node):
        try:
            self.visit(node)
        except Return as ret:
            return ret.value

    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)

    def generic_visit(self, node):
        raise RuntimeError(f"No interpreter rule for {type(node).__name__}")

    def execute_block(self, statements, env):
        previous = self.env
        try:
            self.env = env
            for statement in statements:
                self.visit(statement)
        finally:
            self.env = previous

    def is_true(self, value):
        return bool(value)

    def visit_ProgramNode(self, node):
        for statement in node.statements:
            self.visit(statement)

    def visit_BlockNode(self, node):
        self.execute_block(node.statements, Environment(self.env))

    def visit_LetNode(self, node):
        value = None
        if node.value is not None:
            value = self.visit(node.value)
        self.env.define(node.name, value)

    def visit_AssignNode(self, node):
        if not isinstance(node.target, IdentifierNode):
            raise RuntimeError("Assignment target must be a variable")

        name = node.target.value
        current = self.env.get(name)
        value = self.visit(node.value)

        if node.op == "EQ":
            new_value = value
        elif node.op == "ADEQ":
            new_value = current + value
        elif node.op == "MSEQ":
            new_value = current - value
        elif node.op == "MULEQ":
            new_value = current * value
        elif node.op == "DIVEQ":
            new_value = current / value
        elif node.op == "MODEQ":
            new_value = current % value
        else:
            raise RuntimeError(f"Assignment operator '{node.op}' is not supported")

        self.env.set(name, new_value)
        return new_value

    def visit_OutputNode(self, node):
        values = [self.visit(value) for value in node.values]
        print(*values)

    def visit_ReturnNode(self, node):
        value = None
        if node.value is not None:
            value = self.visit(node.value)
        raise Return(value)

    def visit_IfNode(self, node):
        if self.is_true(self.visit(node.condition)):
            self.visit(node.body)
            return

        for condition, body in node.elifs:
            if self.is_true(self.visit(condition)):
                self.visit(body)
                return

        if node.else_body is not None:
            self.visit(node.else_body)

    def visit_WhileNode(self, node):
        while self.is_true(self.visit(node.condition)):
            self.visit(node.body)

    def visit_ForNode(self, node):
        iterable = self.visit(node.iterable)
        if not hasattr(iterable, "__iter__"):
            raise RuntimeError("For loop value is not iterable")

        for item in iterable:
            loop_env = Environment(self.env)
            loop_env.define(node.name, item)
            self.execute_block(node.body.statements, loop_env)

    def visit_FunctionNode(self, node):
        function = UserFunction(node, self.env)
        self.env.define(node.name, function)

    def visit_ExprStatementNode(self, node):
        return self.visit(node.expr)

    def visit_NumberNode(self, node):
        return node.value

    def visit_StringNode(self, node):
        return node.value

    def visit_IdentifierNode(self, node):
        return self.env.get(node.value)

    def visit_CallNode(self, node):
        callee = self.visit(node.callee)
        args = [self.visit(arg) for arg in node.args]

        if isinstance(callee, UserFunction):
            return callee.call(self, args)
        if callable(callee):
            return callee(*args)

        raise RuntimeError("Can only call functions")

    def visit_BinaryOpNode(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        if node.op == "ADD":
            return left + right
        if node.op == "MINUS":
            return left - right
        if node.op == "MULTIPLY":
            return left * right
        if node.op == "DIVIDE":
            return left / right
        if node.op == "MODULO":
            return left % right
        if node.op == "EQEQ":
            return left == right
        if node.op == "NEQ":
            return left != right
        if node.op == "GT":
            return left > right
        if node.op == "LS":
            return left < right
        if node.op == "GTEQ":
            return left >= right
        if node.op == "LSEQ":
            return left <= right
        if node.op == "AND":
            return bool(left) and bool(right)
        if node.op == "OR":
            return bool(left) or bool(right)
        if node.op == "XOR":
            return bool(left) ^ bool(right)

        raise RuntimeError(f"Unsupported operator '{node.op}'")

    def visit_UnaryOpNode(self, node):
        if node.op == "ADD":
            return +self.visit(node.right)
        if node.op == "MINUS":
            return -self.visit(node.right)
        if node.op == "NOT":
            return not self.visit(node.right)

        if node.op == "PRE_INC":
            return self.increment(node.right, 1, prefix=True)
        if node.op == "PRE_DEC":
            return self.increment(node.right, -1, prefix=True)
        if node.op == "POST_INC":
            return self.increment(node.right, 1, prefix=False)
        if node.op == "POST_DEC":
            return self.increment(node.right, -1, prefix=False)

        raise RuntimeError(f"Unsupported unary operator '{node.op}'")

    def increment(self, target, amount, prefix):
        if not isinstance(target, IdentifierNode):
            raise RuntimeError("++ and -- expect an identifier")

        name = target.value
        old_value = self.env.get(name)
        new_value = old_value + amount
        self.env.set(name, new_value)
        if prefix:
            return new_value
        return old_value
