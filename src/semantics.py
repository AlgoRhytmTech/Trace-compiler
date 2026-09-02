from .ast import *
from .tokens import Token
from .semantic.types import Type, TypeKind, INT_TYPE, FLOAT_TYPE, STRING_TYPE, BOOL_TYPE, VOID_TYPE, UNKNOWN_TYPE, BOOL_TYPE, NULL_TYPE
from typing import Optional
from .semantic.diagnostics import Diagnostic, Emitter, SourceLocation

class SymbolInfo:
    def __init__(self, kind: str, type: Type = None,
                 param_count: int = None,
                 function_ast: Optional[FunctionNode] = None):
        self.kind = kind          # 'variable', 'function', 'parameter', 'builtin'
        self.type = type          # Type of the variable or function return
        self.param_count = param_count  # For functions: number of parameters
        self.function_ast = function_ast  # For function symbols (defining AST node)
        # For builtins, we might not have type or param_count, but we can set them if known

class Scope:
    def __init__(self, parent=None):
        self.parent = parent
        self.symbols = {}  # name -> SymbolInfo

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
        self.node_types = {}  # ASTNode -> Type
        self._add_builtins()

    def _add_builtins(self):
        # input: () -> string
        self.global_scope.declare("input", SymbolInfo(
            kind='builtin',
            type=STRING_TYPE,
            param_count=0
        ))
        # output: (any) -> void
        self.global_scope.declare("output", SymbolInfo(
            kind='builtin',
            type=VOID_TYPE,
            param_count=1
        ))
        # We'll add range and len as builtins that we don't check thoroughly
        self.global_scope.declare("range", SymbolInfo(
            kind='builtin',
            type=UNKNOWN_TYPE,  # We don't know the exact type, but we know it's used in for loops
            param_count=1
        ))
        self.global_scope.declare("len", SymbolInfo(
            kind='builtin',
            type=INT_TYPE,  # len returns an integer
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

    # Helper method to check if a type is numeric
    def _is_numeric(self, type_: Type):
        return type_.kind in (TypeKind.INT, TypeKind.FLOAT)

    # Helper method to check if a type is string
    def _is_string(self, type_: Type):
        return type_.kind == TypeKind.STRING

    # Helper method to check if a type is boolean
    def _is_bool(self, type_: Type):
        return type_.kind == TypeKind.BOOL

    # Helper method to check if two types are compatible for assignment
    # We'll consider them compatible if they are the same, or if we are assigning a numeric to a numeric (int to float or float to int)?
    # But note: the interpreter does not allow implicit conversion between int and float in arithmetic?
    # Actually, in the interpreter, if you have an int and a float in an expression, the result is float.
    # However, for assignment, we are going to require exact match for now to keep it simple.
    # We can change this later if needed.

    def _types_compatible(self, left: Type, right: Type):
        return left == right

    # Helper method to get the type of a binary operation
    def _binary_op_type(self, op: str, left: Type, right: Type):
        # First, check if the operation is allowed
        allowed, result_type = self._check_binary_op(op, left, right)
        if not allowed:
            return None
        return result_type

    def _check_binary_op(self, op: str, left: Type, right: Type):
        # Check if the operation is allowed for the given types
        if op in ("ADD", "MINUS", "MULTIPLY", "DIVIDE", "MODULO"):
            # These are arithmetic operations
            if self._is_numeric(left) and self._is_numeric(right):
                # Both are numeric
                if op == "ADD":
                    # If either is float, result is float
                    if left.kind == TypeKind.FLOAT or right.kind == TypeKind.FLOAT:
                        return True, FLOAT_TYPE
                    else:
                        return True, INT_TYPE
                elif op == "MINUS":
                    if left.kind == TypeKind.FLOAT or right.kind == TypeKind.FLOAT:
                        return True, FLOAT_TYPE
                    else:
                        return True, INT_TYPE
                elif op == "MULTIPLY":
                    if left.kind == TypeKind.FLOAT or right.kind == TypeKind.FLOAT:
                        return True, FLOAT_TYPE
                    else:
                        return True, INT_TYPE
                elif op == "DIVIDE":
                    # Division always returns float
                    return True, FLOAT_TYPE
                elif op == "MODULO":
                    # Modulo requires integers
                    if left.kind == TypeKind.INT and right.kind == TypeKind.INT:
                        return True, INT_TYPE
                    else:
                        return False, None
            elif op == "ADD" and self._is_string(left) and self._is_string(right):
                # String concatenation
                return True, STRING_TYPE
            elif op == "MULTIPLY" and ((self._is_string(left) and self._is_numeric(right)) or
                                       (self._is_numeric(left) and self._is_string(right))):
                # String repetition
                return True, STRING_TYPE
            else:
                return False, None
        elif op in ("EQEQ", "NEQ"):
            # Equality and inequality: any types allowed
            return True, BOOL_TYPE
        elif op in ("GT", "LS", "GTEQ", "LSEQ"):
            # Comparison: only allowed if both are numeric or both are strings
            if (self._is_numeric(left) and self._is_numeric(right)) or \
               (self._is_string(left) and self._is_string(right)):
                return True, BOOL_TYPE
            else:
                return False, None
        elif op in ("AND", "OR", "XOR"):
            # Logical operations: any types allowed (they are converted to bool)
            return True, BOOL_TYPE
        else:
            return False, None

    # Helper method to get the type of a unary operation
    def _unary_op_type(self, op: str, operand: Type):
        allowed, result_type = self._check_unary_op(op, operand)
        if not allowed:
            return None
        return result_type

    def _check_unary_op(self, op: str, operand: Type):
        if op in ("ADD", "MINUS"):
            if self._is_numeric(operand):
                if operand.kind == TypeKind.FLOAT:
                    return True, FLOAT_TYPE
                else:
                    return True, INT_TYPE
            else:
                return False, None
        elif op == "NOT":
            # Any type allowed, returns bool
            return True, BOOL_TYPE
        else:
            return False, None

    # Expression visitors
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
            # The type of the LetNode is the type of the value
            self.node_types[node] = self.node_types.get(node.value, UNKNOWN_TYPE)
        else:
            # If no value, we don't know the type yet. We'll mark it as unknown.
            # When it is assigned later, we will update the variable's type.
            self.node_types[node] = UNKNOWN_TYPE
        # Declare the variable in the current scope
        # We don't know the type yet if there's no value, so we'll use UNKNOWN_TYPE
        # When we assign to it later, we will update the symbol table.
        var_type = self.node_types.get(node.value, UNKNOWN_TYPE) if node.value is not None else UNKNOWN_TYPE
        self.current_scope.declare(node.name, SymbolInfo(
            kind='variable',
            type=var_type
        ))

    def visit_AssignNode(self, node):
        if not isinstance(node.target, IdentifierNode):
            self.emitter.error(
                "Left side must be an identifier",
                SourceLocation("", node.target.line, node.target.col) if hasattr(node.target, 'line') else SourceLocation("", 0, 0)
            )
            return
        # First, visit the value to get its type
        self.visit(node.value)
        value_type = self.node_types.get(node.value, UNKNOWN_TYPE)
        # Look up the variable in the current scope
        symbol = self.current_scope.lookup(node.target.value)
        if symbol is None:
            self.emitter.error(
                f"Undefined variable '{node.target.value}'",
                SourceLocation("", node.target.line, node.target.col)
            )
            return
        # Check if the variable's type is compatible with the value's type
        if symbol.type == UNKNOWN_TYPE:
            # We don't know the variable's type yet, so we set it to the value's type
            symbol.type = value_type
        elif not self._types_compatible(symbol.type, value_type):
            self.emitter.error(
                f"Type mismatch: cannot assign {value_type} to variable '{node.target.value}' of type {symbol.type}",
                SourceLocation("", node.target.line, node.target.col)
            )
            return
        # Update the variable's type if we learned something new
        if symbol.type == UNKNOWN_TYPE:
            symbol.type = value_type
        # Store the type of the assignment node (optional)
        self.node_types[node] = value_type

    def visit_OutputNode(self, node):
        for value in node.values:
            self.visit(value)
        # Output does not produce a value, so we don't set a type for the node

    def visit_ReturnNode(self, node):
        if node.value is not None:
            self.visit(node.value)
            self.node_types[node] = self.node_types.get(node.value, UNKNOWN_TYPE)
        else:
            self.node_types[node] = VOID_TYPE

    def visit_IfNode(self, node):
        self.visit(node.condition)
        # Condition can be any type (interpreter converts to bool)
        self.visit(node.body)
        for elif_condition, elif_body in node.elifs:
            self.visit(elif_condition)
            self.visit(elif_body)
        if node.else_body is not None:
            self.visit(node.else_body)

    def visit_WhileNode(self, node):
        self.visit(node.condition)
        # Condition can be any type
        self.visit(node.body)

    def visit_ForNode(self, node):
        self.visit(node.iterable)
        # The iterable can be any type that is iterable (we don't check)
        self.push_scope()
        # The loop variable is a new variable in the loop scope
        # We don't know its type yet, so we'll mark it as unknown
        self.current_scope.declare(node.name, SymbolInfo(
            kind='variable',
            type=UNKNOWN_TYPE
        ))
        self.visit(node.body)
        self.pop_scope()

    def visit_FunctionNode(self, node):
        # Declare the function in the current scope
        # We don't know the return type yet, so we'll use UNKNOWN_TYPE
        # We also don't know the parameter types, so we'll set them to UNKNOWN_TYPE when we declare them
        func_symbol = SymbolInfo(
            kind='function',
            type=UNKNOWN_TYPE,  # Return type unknown
            param_count=len(node.params),
            function_ast=node
        )
        self.current_scope.declare(node.name, func_symbol)

        old_function = self.current_function
        self.current_function = node
        self.push_scope()

        # Declare the parameters
        for param in node.params:
            # Parameters are variables in the function scope
            # We don't know their type yet, so we'll mark them as unknown
            self.current_scope.declare(param, SymbolInfo(
                kind='parameter',
                type=UNKNOWN_TYPE
            ))
        self.visit(node.body)

        self.pop_scope()
        self.current_function = old_function

        # After visiting the body, we might have learned the return type from return statements
        # But we don't have a way to collect that information easily.
        # For now, we'll leave the function's return type as UNKNOWN_TYPE.
        # We could update it by looking at the return statements, but we'll skip that for simplicity.

    def visit_ExprStatementNode(self, node):
        self.visit(node.expr)

    def visit_NumberNode(self, node):
        # Determine if it's int or float
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
                SourceLocation("", node.line, node.col)
            )
            self.node_types[node] = UNKNOWN_TYPE
        else:
            self.node_types[node] = symbol.type
        return self.node_types[node]

    def visit_CallNode(self, node):
        # First, visit the callee to get its symbol (if it's an identifier)
        self.visit(node.callee)
        # Check if the callee is an identifier and look it up
        if isinstance(node.callee, IdentifierNode):
            symbol = self.current_scope.lookup(node.callee.value)
            if symbol is None:
                # Special case for built-in input (we already added it)
                if node.callee.value == "input":
                    # We know input is a built-in
                    symbol = SymbolInfo(
                        kind='builtin',
                        type=STRING_TYPE,
                        param_count=0
                    )
                else:
                    self.emitter.error(
                        f"Undefined function '{node.callee.value}'",
                        SourceLocation("", node.callee.line, node.callee.col)
                    )
                    self.node_types[node] = UNKNOWN_TYPE
                    return
            # Check the number of arguments
            if symbol.param_count is not None and len(node.args) != symbol.param_count:
                self.emitter.error(
                    f"Function '{node.callee.value}' expects {symbol.param_count} arguments but got {len(node.args)}",
                    SourceLocation("", node.callee.line, node.callee.col)
                )
            # We don't check the types of the arguments because we don't have parameter types
            for arg in node.args:
                self.visit(arg)
            # Set the type of the call node
            if symbol.kind == 'builtin' and symbol.type == STRING_TYPE:
                # Special case for input
                self.node_types[node] = symbol.type
            else:
                # For user-defined functions, we don't know the return type
                self.node_types[node] = UNKNOWN_TYPE
        else:
            # The callee is an expression (e.g., a function variable)
            # We don't support function pointers in this language, so we'll treat it as an error
            self.emitter.error(
                "Function call expression not supported",
                SourceLocation("", node.callee.line, node.callee.col)
            )
            self.node_types[node] = UNKNOWN_TYPE
            return

    def visit_BinaryOpNode(self, node):
        self.visit(node.left)
        self.visit(node.right)
        left_type = self.node_types.get(node.left, UNKNOWN_TYPE)
        right_type = self.node_types.get(node.right, UNKNOWN_TYPE)
        result_type = self._binary_op_type(node.op, left_type, right_type)
        if result_type is None:
            self.emitter.error(
                f"Unsupported operation '{node.op}' between types '{left_type}' and '{right_type}'",
                SourceLocation("", node.line, node.col)
            )
            self.node_types[node] = UNKNOWN_TYPE
        else:
            self.node_types[node] = result_type

    def visit_UnaryOpNode(self, node):
        self.visit(node.right)
        operand_type = self.node_types.get(node.right, UNKNOWN_TYPE)
        result_type = self._unary_op_type(node.op, operand_type)
        if result_type is None:
            self.emitter.error(
                f"Unsupported unary operation '{node.op}' on type '{operand_type}'",
                SourceLocation("", node.line, node.col)
            )
            self.node_types[node] = UNKNOWN_TYPE
        else:
            self.node_types[node] = result_type

# End of file