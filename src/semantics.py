from .ast import *
from .semantic.types import (
    Type, TypeKind,
    INT_TYPE, FLOAT_TYPE, STRING_TYPE, BOOL_TYPE,
    VOID_TYPE, UNKNOWN_TYPE, NULL_TYPE
)
from typing import Optional
from .semantic.diagnostics import Emitter, SourceLocation


class SymbolInfo:
    def __init__(self, kind: str, type: Type = None,
                 param_count: int = None,
                 function_ast: Optional[FunctionNode] = None):
        self.kind = kind
        self.type = type
        self.param_count = param_count
        self.function_ast = function_ast


class Scope:
    def __init__(self, parent=None):
        self.parent = parent
        self.symbols = {}

    def declare(self, name: str, info: SymbolInfo):
        if name in self.symbols:
            raise SemanticsError(f"Duplicate symbol {name}")
        self.symbols[name] = info

    def lookup(self, name: str):
        scope = self
        while scope is not None:
            if name in scope.symbols:
                return scope.symbols[name]
            scope = scope.parent
        return None


class SemanticAnalyzer:
    def __init__(self, file=""):
        self.global_scope = Scope()
        self.current_scope = self.global_scope
        self.current_function = None
        self.file = file
        self.emitter = Emitter()
        self.node_types = {}
        self.current_return_types = []
        self._add_builtins()

    def _add_builtins(self):
        self.global_scope.declare("input", SymbolInfo(
            kind="builtin",
            type=STRING_TYPE,
            param_count=0
        ))

        self.global_scope.declare("output", SymbolInfo(
            kind="builtin",
            type=VOID_TYPE,
            param_count=1
        ))

        self.global_scope.declare("range", SymbolInfo(
            kind="builtin",
            type=INT_TYPE,
            param_count=2
        ))

        self.global_scope.declare("len", SymbolInfo(
            kind="builtin",
            type=INT_TYPE,
            param_count=1
        ))

    def analyze(self, node):
        self.visit(node)
        return self.emitter

    def push_scope(self):
        self.current_scope = Scope(self.current_scope)

    def pop_scope(self):
        self.current_scope = self.current_scope.parent

    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)

    def generic_visit(self, node):
        raise SemanticsError(f"Unhandled node {type(node).__name__}")

    def _is_numeric(self, type_):
        return type_.kind in (TypeKind.INT, TypeKind.FLOAT)

    def _is_string(self, type_):
        return type_.kind == TypeKind.STRING

    def _is_bool(self, type_):
        return type_.kind == TypeKind.BOOL

    def _types_compatible(self, left, right):
        if left == UNKNOWN_TYPE or right == UNKNOWN_TYPE:
            return True
        return left == right

    def _binary_op_type(self, op, left, right):
        allowed, result_type = self._check_binary_op(op, left, right)

        if not allowed:
            return None

        return result_type

    def _check_binary_op(self, op, left, right):

        if left == UNKNOWN_TYPE or right == UNKNOWN_TYPE:
            return True, UNKNOWN_TYPE

        if op in ("ADD", "MINUS", "MULTIPLY", "DIVIDE", "MODULO"):

            if self._is_numeric(left) and self._is_numeric(right):

                if op == "ADD":
                    if left.kind == TypeKind.FLOAT or right.kind == TypeKind.FLOAT:
                        return True, FLOAT_TYPE
                    return True, INT_TYPE

                if op == "MINUS":
                    if left.kind == TypeKind.FLOAT or right.kind == TypeKind.FLOAT:
                        return True, FLOAT_TYPE
                    return True, INT_TYPE

                if op == "MULTIPLY":
                    if left.kind == TypeKind.FLOAT or right.kind == TypeKind.FLOAT:
                        return True, FLOAT_TYPE
                    return True, INT_TYPE

                if op == "DIVIDE":
                    return True, FLOAT_TYPE

                if op == "MODULO":
                    if left.kind == TypeKind.INT and right.kind == TypeKind.INT:
                        return True, INT_TYPE
                    return False, None

            elif op == "ADD" and self._is_string(left) and self._is_string(right):
                return True, STRING_TYPE

            elif op == "MULTIPLY" and (
                (self._is_string(left) and self._is_numeric(right)) or
                (self._is_numeric(left) and self._is_string(right))
            ):
                return True, STRING_TYPE

            return False, None

        if op in ("EQEQ", "NEQ"):
            return True, BOOL_TYPE

        if op in ("GT", "LS", "GTEQ", "LSEQ"):
            if (
                self._is_numeric(left) and self._is_numeric(right)
            ) or (
                self._is_string(left) and self._is_string(right)
            ):
                return True, BOOL_TYPE

            return False, None

        if op in ("AND", "OR", "XOR"):
            return True, BOOL_TYPE

        return False, None

    def _unary_op_type(self, op, operand):
        allowed, result_type = self._check_unary_op(op, operand)

        if not allowed:
            return None

        return result_type

    def _check_unary_op(self, op, operand):

        if operand == UNKNOWN_TYPE:
            return True, UNKNOWN_TYPE

        if op in ("ADD", "MINUS"):
            if self._is_numeric(operand):
                if operand.kind == TypeKind.FLOAT:
                    return True, FLOAT_TYPE
                return True, INT_TYPE

            return False, None

        if op == "NOT":
            return True, BOOL_TYPE

        return False, None

    def visit_ProgramNode(self, node):
        for statement in node.statements:
            self.visit(statement)

    def visit_BlockNode(self, node):
        self.push_scope()

        for statement in node.statements:
            self.visit(statement)

        self.pop_scope()

    def visit_LetNode(self, node):
        if node.value is not None:
            self.visit(node.value)
            value_type = self.node_types.get(node.value, UNKNOWN_TYPE)
            self.node_types[node] = value_type
        else:
            value_type = UNKNOWN_TYPE
            self.node_types[node] = UNKNOWN_TYPE

        self.current_scope.declare(
            node.name,
            SymbolInfo(
                kind="variable",
                type=value_type
            )
        )

    def visit_AssignNode(self, node):

        if not isinstance(node.target, IdentifierNode):
            self.emitter.error(
                "Left side must be an identifier",
                SourceLocation(
                    self.file,
                    getattr(node.target, "line", 0),
                    getattr(node.target, "col", 0)
                )
            )
            return

        self.visit(node.value)

        value_type = self.node_types.get(
            node.value,
            UNKNOWN_TYPE
        )

        symbol = self.current_scope.lookup(node.target.value)

        if symbol is None:
            self.emitter.error(
                f"Undefined variable '{node.target.value}'",
                SourceLocation(
                    self.file,
                    node.target.line,
                    node.target.col
                )
            )
            return

        if symbol.type == UNKNOWN_TYPE:
            symbol.type = value_type

        elif not self._types_compatible(symbol.type, value_type):
            self.emitter.error(
                f"Type mismatch: cannot assign {value_type} "
                f"to variable '{node.target.value}' "
                f"of type {symbol.type}",
                SourceLocation(
                    self.file,
                    node.target.line,
                    node.target.col
                )
            )
            return

        self.node_types[node] = value_type

    def visit_OutputNode(self, node):
        for value in node.values:
            self.visit(value)

    def visit_ReturnNode(self, node):

        if node.value is not None:
            self.visit(node.value)

            return_type = self.node_types.get(
                node.value,
                UNKNOWN_TYPE
            )

            self.node_types[node] = return_type
            self.current_return_types.append(return_type)

        else:
            self.node_types[node] = VOID_TYPE
            self.current_return_types.append(VOID_TYPE)

    def visit_IfNode(self, node):
        self.visit(node.condition)
        self.visit(node.body)

        for elif_condition, elif_body in node.elifs:
            self.visit(elif_condition)
            self.visit(elif_body)

        if node.else_body is not None:
            self.visit(node.else_body)

    def visit_WhileNode(self, node):
        self.visit(node.condition)
        self.visit(node.body)

    def visit_ForNode(self, node):
        self.visit(node.iterable)

        loop_type = UNKNOWN_TYPE

        if isinstance(node.iterable, CallNode):
            if isinstance(node.iterable.callee, IdentifierNode):
                if node.iterable.callee.value == "range":
                    loop_type = INT_TYPE

        self.push_scope()

        self.current_scope.declare(
            node.name,
            SymbolInfo(
                kind="variable",
                type=loop_type
            )
        )

        self.visit(node.body)

        self.pop_scope()

    def visit_FunctionNode(self, node):

        func_symbol = SymbolInfo(
            kind="function",
            type=UNKNOWN_TYPE,
            param_count=len(node.params),
            function_ast=node
        )

        self.current_scope.declare(
            node.name,
            func_symbol
        )

        old_function = self.current_function
        old_return_types = self.current_return_types

        self.current_function = node
        self.current_return_types = []

        self.push_scope()

        for param in node.params:
            self.current_scope.declare(
                param,
                SymbolInfo(
                    kind="parameter",
                    type=UNKNOWN_TYPE
                )
            )

        self.visit(node.body)

        self.pop_scope()

        self.current_function = old_function
        self.current_return_types = old_return_types

    def visit_ExprStatementNode(self, node):
        self.visit(node.expr)

    def visit_NumberNode(self, node):
        if isinstance(node.value, float):
            self.node_types[node] = FLOAT_TYPE
        else:
            self.node_types[node] = INT_TYPE

    def visit_StringNode(self, node):
        self.node_types[node] = STRING_TYPE

    def visit_BooleanNode(self, node):
        self.node_types[node] = BOOL_TYPE

    def visit_NullNode(self, node):
        self.node_types[node] = NULL_TYPE

    def visit_IdentifierNode(self, node):

        symbol = self.current_scope.lookup(node.value)

        if symbol is None:
            self.emitter.error(
                f"Undefined variable '{node.value}'",
                SourceLocation(
                    self.file,
                    node.line,
                    node.col
                )
            )

            self.node_types[node] = UNKNOWN_TYPE

        else:
            self.node_types[node] = symbol.type

        return self.node_types[node]

    def visit_CallNode(self, node):

        if not isinstance(node.callee, IdentifierNode):
            self.emitter.error(
                "Function call expression not supported",
                SourceLocation(
                    self.file,
                    node.callee.line,
                    node.callee.col
                )
            )

            self.node_types[node] = UNKNOWN_TYPE
            return

        function_name = node.callee.value

        symbol = self.current_scope.lookup(function_name)

        if symbol is None:
            self.emitter.error(
                f"Undefined function '{function_name}'",
                SourceLocation(
                    self.file,
                    node.callee.line,
                    node.callee.col
                )
            )

            self.node_types[node] = UNKNOWN_TYPE
            return

        if (
            symbol.param_count is not None
            and len(node.args) != symbol.param_count
        ):
            self.emitter.error(
                f"Function '{function_name}' expects "
                f"{symbol.param_count} arguments but got "
                f"{len(node.args)}",
                SourceLocation(
                    self.file,
                    node.callee.line,
                    node.callee.col
                )
            )

        for arg in node.args:
            self.visit(arg)

        if symbol.kind == "builtin":
            self.node_types[node] = symbol.type
            return

        if symbol.kind != "function" or symbol.function_ast is None:
            self.node_types[node] = UNKNOWN_TYPE
            return

        function_node = symbol.function_ast

        old_scope = self.current_scope
        old_function = self.current_function
        old_return_types = self.current_return_types

        function_scope = Scope(self.global_scope)

        for i, param in enumerate(function_node.params):
            param_type = UNKNOWN_TYPE

            if i < len(node.args):
                param_type = self.node_types.get(
                    node.args[i],
                    UNKNOWN_TYPE
                )

            function_scope.declare(
                param,
                SymbolInfo(
                    kind="parameter",
                    type=param_type
                )
            )

        self.current_scope = function_scope
        self.current_function = function_node
        self.current_return_types = []

        self.visit(function_node.body)

        return_types = self.current_return_types[:]

        self.current_scope = old_scope
        self.current_function = old_function
        self.current_return_types = old_return_types

        if return_types:
            result_type = return_types[0]

            for return_type in return_types[1:]:
                if return_type != result_type:
                    result_type = UNKNOWN_TYPE
                    break

            symbol.type = result_type
            self.node_types[node] = result_type

        else:
            symbol.type = VOID_TYPE
            self.node_types[node] = VOID_TYPE

    def visit_BinaryOpNode(self, node):

        self.visit(node.left)
        self.visit(node.right)

        left_type = self.node_types.get(
            node.left,
            UNKNOWN_TYPE
        )

        right_type = self.node_types.get(
            node.right,
            UNKNOWN_TYPE
        )

        result_type = self._binary_op_type(
            node.op,
            left_type,
            right_type
        )

        if result_type is None:
            self.emitter.error(
                f"Unsupported operation '{node.op}' "
                f"between types '{left_type}' "
                f"and '{right_type}'",
                SourceLocation(
                    self.file,
                    node.line,
                    node.col
                )
            )

            self.node_types[node] = UNKNOWN_TYPE

        else:
            self.node_types[node] = result_type

    def visit_UnaryOpNode(self, node):

        self.visit(node.right)

        operand_type = self.node_types.get(
            node.right,
            UNKNOWN_TYPE
        )

        result_type = self._unary_op_type(
            node.op,
            operand_type
        )

        if result_type is None:
            self.emitter.error(
                f"Unsupported unary operation '{node.op}' "
                f"on type '{operand_type}'",
                SourceLocation(
                    self.file,
                    node.line,
                    node.col
                )
            )

            self.node_types[node] = UNKNOWN_TYPE

        else:
            self.node_types[node] = result_type