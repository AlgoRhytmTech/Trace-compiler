from dataclasses import dataclass, field
from typing import Any, Optional

from .ast import *


@dataclass(frozen=True)
class IRValue:
    name: str

    def __repr__(self):
        return self.name


@dataclass(frozen=True, repr=False)
class IRTemp(IRValue):
    pass


@dataclass(frozen=True, repr=False)
class IRVariable(IRValue):
    pass


@dataclass(frozen=True)
class IRConstant:
    value: Any

    def __repr__(self):
        return repr(self.value)


@dataclass(frozen=True)
class IRLabel:
    name: str

    def __repr__(self):
        return self.name


@dataclass(frozen=True)
class IRInstruction:
    pass


@dataclass(frozen=True)
class IRLabelInstr(IRInstruction):
    label: IRLabel

    def __repr__(self):
        return f"{self.label}:"


@dataclass(frozen=True)
class IRAssign(IRInstruction):
    target: Any
    value: Any

    def __repr__(self):
        return f"{self.target} = {self.value}"


@dataclass(frozen=True)
class IRBinaryOp(IRInstruction):
    target: IRTemp
    op: str
    left: Any
    right: Any

    def __repr__(self):
        return f"{self.target} = {self.op} {self.left}, {self.right}"


@dataclass(frozen=True)
class IRUnaryOp(IRInstruction):
    target: IRTemp
    op: str
    operand: Any

    def __repr__(self):
        return f"{self.target} = {self.op} {self.operand}"


@dataclass(frozen=True)
class IRJump(IRInstruction):
    target: IRLabel

    def __repr__(self):
        return f"jump {self.target}"


@dataclass(frozen=True)
class IRBranch(IRInstruction):
    condition: Any
    true_label: IRLabel
    false_label: IRLabel

    def __repr__(self):
        return f"branch {self.condition}, {self.true_label}, {self.false_label}"


@dataclass(frozen=True)
class IRCall(IRInstruction):
    target: Optional[IRTemp]
    callee: str
    args: list[Any] = field(default_factory=list)

    def __repr__(self):
        args = ", ".join(map(str, self.args))
        if self.target is None:
            return f"call {self.callee}({args})"
        return f"{self.target} = call {self.callee}({args})"


@dataclass(frozen=True)
class IRReturn(IRInstruction):
    value: Optional[Any] = None

    def __repr__(self):
        if self.value is None:
            return "return"
        return f"return {self.value}"


@dataclass(frozen=True)
class IRIteratorInit(IRInstruction):
    target: IRTemp
    iterable: Any

    def __repr__(self):
        return f"{self.target} = iter {self.iterable}"


@dataclass(frozen=True)
class IRIteratorNext(IRInstruction):
    target: IRVariable
    iterator: IRTemp
    has_value: IRTemp

    def __repr__(self):
        return f"{self.has_value}, {self.target} = next {self.iterator}"


@dataclass
class IRFunction:
    name: str
    params: list[str]
    instructions: list[IRInstruction] = field(default_factory=list)

    def __repr__(self):
        body = "\n  ".join(map(str, self.instructions))
        if body:
            body = "\n  " + body
        return f"function {self.name}({', '.join(self.params)}){body}"


@dataclass
class IRProgram:
    instructions: list[IRInstruction] = field(default_factory=list)
    functions: list[IRFunction] = field(default_factory=list)

    def __repr__(self):
        parts = []
        if self.instructions:
            parts.append("main\n  " + "\n  ".join(map(str, self.instructions)))
        parts.extend(map(str, self.functions))
        return "\n".join(parts)


class IRLoweringError(Exception):
    pass


class TraceIRLowerer:
    def __init__(self):
        self.temp_count = 0
        self.label_count = 0
        self.program = IRProgram()
        self.instructions = self.program.instructions

    def lower(self, node):
        self.visit(node)
        return self.program

    def emit(self, instruction):
        self.instructions.append(instruction)
        return instruction

    def new_temp(self):
        self.temp_count += 1
        return IRTemp(f"%t{self.temp_count}")

    def new_label(self, prefix="L"):
        self.label_count += 1
        return IRLabel(f"{prefix}{self.label_count}")

    def variable(self, name):
        return IRVariable(name)

    def visit(self, node):
        method_name = f"lower_{type(node).__name__}"
        method = getattr(self, method_name, None)
        if method is None:
            raise IRLoweringError(f"Unhandled AST node type: {type(node).__name__}")
        return method(node)

    def lower_ProgramNode(self, node):
        for statement in node.statements:
            self.visit(statement)

    def lower_BlockNode(self, node):
        for statement in node.statements:
            self.visit(statement)

    def lower_LetNode(self, node):
        value = IRConstant(None)
        if node.value is not None:
            value = self.visit(node.value)
        self.emit(IRAssign(self.variable(node.name), value))

    def lower_AssignNode(self, node):
        if not isinstance(node.target, IdentifierNode):
            raise IRLoweringError("Assignment target must be an identifier")

        target = self.variable(node.target.value)
        value = self.visit(node.value)
        if node.op == "EQ":
            self.emit(IRAssign(target, value))
            return target

        op_map = {
            "ADEQ": "ADD",
            "MSEQ": "MINUS",
            "MULEQ": "MULTIPLY",
            "DIVEQ": "DIVIDE",
            "MODEQ": "MODULO",
        }
        if node.op not in op_map:
            raise IRLoweringError(f"Unsupported assignment operator: {node.op}")

        result = self.new_temp()
        self.emit(IRBinaryOp(result, op_map[node.op], target, value))
        self.emit(IRAssign(target, result))
        return target

    def lower_OutputNode(self, node):
        args = [self.visit(value) for value in node.values]
        self.emit(IRCall(None, "output", args))

    def lower_ReturnNode(self, node):
        value = None
        if node.value is not None:
            value = self.visit(node.value)
        self.emit(IRReturn(value))

    def lower_ExprStatementNode(self, node):
        return self.visit(node.expr)

    def lower_IfNode(self, node):
        end_label = self.new_label("if_end")
        then_label = self.new_label("if_then")
        false_label = self.new_label("if_next")

        condition = self.visit(node.condition)
        self.emit(IRBranch(condition, then_label, false_label))
        self.emit(IRLabelInstr(then_label))
        self.visit(node.body)
        self.emit(IRJump(end_label))
        self.emit(IRLabelInstr(false_label))

        for elif_condition, elif_body in node.elifs:
            next_label = self.new_label("if_next")
            body_label = self.new_label("elif")
            condition = self.visit(elif_condition)
            self.emit(IRBranch(condition, body_label, next_label))
            self.emit(IRLabelInstr(body_label))
            self.visit(elif_body)
            self.emit(IRJump(end_label))
            self.emit(IRLabelInstr(next_label))

        if node.else_body is not None:
            self.visit(node.else_body)
        self.emit(IRLabelInstr(end_label))

    def lower_WhileNode(self, node):
        start_label = self.new_label("while_start")
        body_label = self.new_label("while_body")
        end_label = self.new_label("while_end")

        self.emit(IRLabelInstr(start_label))
        condition = self.visit(node.condition)
        self.emit(IRBranch(condition, body_label, end_label))
        self.emit(IRLabelInstr(body_label))
        self.visit(node.body)
        self.emit(IRJump(start_label))
        self.emit(IRLabelInstr(end_label))

    def lower_ForNode(self, node):
        iterator = self.new_temp()
        has_value = self.new_temp()
        start_label = self.new_label("for_start")
        body_label = self.new_label("for_body")
        end_label = self.new_label("for_end")

        iterable = self.visit(node.iterable)
        self.emit(IRIteratorInit(iterator, iterable))
        self.emit(IRLabelInstr(start_label))
        self.emit(IRIteratorNext(self.variable(node.name), iterator, has_value))
        self.emit(IRBranch(has_value, body_label, end_label))
        self.emit(IRLabelInstr(body_label))
        self.visit(node.body)
        self.emit(IRJump(start_label))
        self.emit(IRLabelInstr(end_label))

    def lower_FunctionNode(self, node):
        saved_instructions = self.instructions
        function = IRFunction(node.name, list(node.params))
        self.program.functions.append(function)
        self.instructions = function.instructions
        self.visit(node.body)
        if not self.instructions or not isinstance(self.instructions[-1], IRReturn):
            self.emit(IRReturn(None))
        self.instructions = saved_instructions

    def lower_NumberNode(self, node):
        return IRConstant(node.value)

    def lower_StringNode(self, node):
        return IRConstant(node.value)
    def lower_BooleanNode(self, node):
        return IRConstant(node.value)
    def lower_NullNode(self, node):
        return IRConstant(None)
    
    def lower_IdentifierNode(self, node):
        return self.variable(node.value)

    def lower_CallNode(self, node):
        if not isinstance(node.callee, IdentifierNode):
            raise IRLoweringError("Only direct function calls are supported")

        args = [self.visit(arg) for arg in node.args]
        result = self.new_temp()
        self.emit(IRCall(result, node.callee.value, args))
        return result

    def lower_BinaryOpNode(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        result = self.new_temp()
        self.emit(IRBinaryOp(result, node.op, left, right))
        return result

    def lower_UnaryOpNode(self, node):
        if node.op in ("PRE_INC", "PRE_DEC", "POST_INC", "POST_DEC"):
            return self.lower_increment(node)

        operand = self.visit(node.right)
        result = self.new_temp()
        self.emit(IRUnaryOp(result, node.op, operand))
        return result

    def lower_increment(self, node):
        if not isinstance(node.right, IdentifierNode):
            raise IRLoweringError("++ and -- require an identifier")

        target = self.variable(node.right.value)
        old_value = self.new_temp()
        self.emit(IRAssign(old_value, target))

        op = "ADD" if node.op in ("PRE_INC", "POST_INC") else "MINUS"
        new_value = self.new_temp()
        self.emit(IRBinaryOp(new_value, op, old_value, IRConstant(1)))
        self.emit(IRAssign(target, new_value))

        if node.op in ("PRE_INC", "PRE_DEC"):
            return new_value
        return old_value


class CodeGen(TraceIRLowerer):
    def generate(self, ast_node):
        return self.lower(ast_node)


def lower_to_ir(ast_node):
    return TraceIRLowerer().lower(ast_node)
