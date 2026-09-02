from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Tuple


class OpCode(str,Enum):
    # Constants / variables
    LOAD_CONST = "LOAD_CONST"
    LOAD_VAR = "LOAD_VAR"
    STORE_VAR = "STORE_VAR"

    # Arithmetic / logical operations
    BINARY = "BINARY"
    UNARY = "UNARY"

    # Control flow
    JUMP = "JUMP"
    JUMP_IF_FALSE = "JUMP_IF_FALSE"
    

    # Functions
    CALL = "CALL"
    RETURN = "RETURN"

    # Iteration
    ITER_INIT = "ITER_INIT"
    ITER_NEXT = "ITER_NEXT"

    # Stack management
    POP = "POP"

@dataclass(frozen=True)
class Instruction:
    opcode: OpCode
    oprands: Tuple[Any,...] = ()

    def __repr__(self):
        if not self.oprands:
            return self.opcode.value
        return f"{self.opcode.value} " + ", ".join(repr(op) for op in self.oprands)
        

@dataclass
class BytecodeFunction:
    name:str
    params: list[str] = field(default_factory=list)
    instructions: list[Instruction] = field(default_factory=list)

    def emit(self,opcode: OpCode, *operands):
        instruction = Instruction(opcode,tuple(operands))
        self.instructions.append(instruction)
        return instruction

    def __repr__(self):
        lines = [
            f"function{self.name}({','.join(self.params)})"
        ]
        for index, instruction in enumerate(self.instructions):
            lines.append(f"{index:04d}: {instruction}")

        return "\n".join(lines)


@dataclass
class BytecodeProgram:
    instructions: list[Instruction] = field(default_factory=list)
    functions: dict[str, BytecodeFunction] = field(default_factory=dict)

    def emit(self, opcode: OpCode, *operands):
        instruction = Instruction(opcode, tuple(operands))
        self.instructions.append(instruction)
        return instruction

    def add_function(self, function: BytecodeFunction):
        self.functions[function.name] = function

    def __repr__(self):
        lines = ["main"]

        for index, instruction in enumerate(self.instructions):
            lines.append(f"  {index:04d}  {instruction}")

        for function in self.functions.values():
            lines.append("")
            lines.append(str(function))

        return "\n".join(lines)

class BytecodeError(Exception):
    pass

@dataclass
class Label:
    name:str
    position: Optional[int] = None


class BytecodeBuilder:
    """
    Small helper used by the IR -> bytecode compiler.

    It allows jumps to reference labels before their final
    instruction addresses are known.
    """

    def __init__(self):
        self.instructions: list[Instruction] = []
        self.labels: dict[str, Label] = {}

    def emit(self, opcode: OpCode, *operands):
        instruction = Instruction(opcode, tuple(operands))
        self.instructions.append(instruction)
        return instruction

    def create_label(self, name: str) -> Label:
        if name in self.labels:
            return self.labels[name]

        label = Label(name)
        self.labels[name] = label
        return label

    def mark(self, label: Label):
        if label.position is not None:
            raise BytecodeError(
                f"Label '{label.name}' has already been marked"
            )

        label.position = len(self.instructions)

    def resolve(self) -> list[Instruction]:
        resolved = []

        for instruction in self.instructions:
            operands = list(instruction.operands)

            for index, operand in enumerate(operands):
                if isinstance(operand, Label):
                    if operand.position is None:
                        raise BytecodeError(
                            f"Unresolved label: {operand.name}"
                        )

                    operands[index] = operand.position

            resolved.append(
                Instruction(
                    instruction.opcode,
                    tuple(operands),
                )
            )

        return resolved