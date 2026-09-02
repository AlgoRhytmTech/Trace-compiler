from .bytecode import (
    BytecodeProgram,
    BytecodeFunction,
    BytecodeError,
    OpCode,
    Label,
)

from .codegen import (
    IRProgram,
    IRLabelInstr,
    IRAssign,
    IRBinaryOp,
    IRUnaryOp,
    IRJump,
    IRBranch,
    IRCall,
    IRReturn,
    IRIteratorInit,
    IRIteratorNext,
    IRConstant,
    IRValue,
)


class BytecodeCompiler:
    def __init__(self):
        self.program = BytecodeProgram()
        self.labels = {}

    def compile(self, ir_program):
        if not isinstance(ir_program, IRProgram):
            raise BytecodeError("Expected an IRProgram")

        self.program = BytecodeProgram()

        for instruction in ir_program.instructions:
            self.compile_instruction(instruction, self.program)

        self.resolve_labels(self.program)

        for function in ir_program.functions:
            self.compile_function(function)

        return self.program

    def compile_function(self, ir_function):
        function = BytecodeFunction(
            ir_function.name,
            list(ir_function.params)
        )

        self.labels = {}

        for instruction in ir_function.instructions:
            self.compile_instruction(instruction, function)

        self.resolve_labels(function)
        self.program.add_function(function)

    def compile_instruction(self, instruction, target):
        if isinstance(instruction, IRLabelInstr):
            label = self.get_label(instruction.label.name)
            label.position = len(target.instructions)
            return

        if isinstance(instruction, IRAssign):
            value = self.load_value(target, instruction.value)

            if isinstance(instruction.target, IRValue):
                target.emit(OpCode.STORE_VAR, instruction.target.name)

            return

        if isinstance(instruction, IRBinaryOp):
            self.load_value(target, instruction.left)
            self.load_value(target, instruction.right)

            target.emit(OpCode.BINARY, instruction.op)

            if isinstance(instruction.target, IRValue):
                target.emit(OpCode.STORE_VAR, instruction.target.name)

            return

        if isinstance(instruction, IRUnaryOp):
            self.load_value(target, instruction.operand)

            target.emit(OpCode.UNARY, instruction.op)

            if isinstance(instruction.target, IRValue):
                target.emit(OpCode.STORE_VAR, instruction.target.name)

            return

        if isinstance(instruction, IRJump):
            label = self.get_label(instruction.target.name)
            target.emit(OpCode.JUMP, label)
            return

        if isinstance(instruction, IRBranch):
            self.load_value(target, instruction.condition)

            false_label = self.get_label(instruction.false_label.name)
            target.emit(OpCode.JUMP_IF_FALSE, false_label)
            return

        if isinstance(instruction, IRCall):
            for arg in instruction.args:
                self.load_value(target, arg)

            target.emit(
                OpCode.CALL,
                instruction.callee,
                len(instruction.args)
            )

            if instruction.target is not None:
                target.emit(
                    OpCode.STORE_VAR,
                    instruction.target.name
                )

            return

        if isinstance(instruction, IRReturn):
            if instruction.value is not None:
                self.load_value(target, instruction.value)

            target.emit(OpCode.RETURN)
            return

        if isinstance(instruction, IRIteratorInit):
            self.load_value(target, instruction.iterable)

            target.emit(
                OpCode.ITER_INIT,
                instruction.target.name
            )
            return

        if isinstance(instruction, IRIteratorNext):
            target.emit(
                OpCode.ITER_NEXT,
                instruction.iterator.name,
                instruction.target.name,
                instruction.has_value.name
            )
            return

        raise BytecodeError(
            f"Unsupported IR instruction: "
            f"{type(instruction).__name__}"
        )

    def load_value(self, target, value):
        if isinstance(value, IRConstant):
            target.emit(OpCode.LOAD_CONST, value.value)
        elif isinstance(value, IRValue):
            target.emit(OpCode.LOAD_VAR, value.name)
        else:
            target.emit(OpCode.LOAD_CONST, value)

    def get_label(self, name):
        if name not in self.labels:
            self.labels[name] = Label(name)

        return self.labels[name]

    def resolve_labels(self, target):
        for instruction in target.instructions:
            for operand in instruction.oprands:
                if isinstance(operand, Label):
                    if operand.position is None:
                        raise BytecodeError(
                            f"Unresolved label: {operand.name}"
                        )

        resolved = []

        for instruction in target.instructions:
            oprands = []

            for operand in instruction.oprands:
                if isinstance(operand, Label):
                    oprands.append(operand.position)
                else:
                    oprands.append(operand)

            resolved.append(
                type(instruction)(
                    instruction.opcode,
                    tuple(oprands)
                )
            )

        target.instructions = resolved