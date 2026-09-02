from .bytecode import BytecodeProgram, BytecodeFunction, Instruction, OpCode


class VMError(Exception):
    pass


class Frame:
    def __init__(self, function, variables=None):
        self.function = function
        self.variables = variables or {}
        self.stack = []
        self.ip = 0
        self.iterators = {}


class VM:
    def __init__(self):
        self.stack = []
        self.globals = {}
        self.call_stack = []

    def run(self, program):
        if not isinstance(program, BytecodeProgram):
            raise VMError("Expected a BytecodeProgram")
        self.functions = program.functions
        
        frame = Frame(
            BytecodeFunction("main", instructions=program.instructions),
            self.globals
        )

        self.call_stack = [frame]

        return self.execute(frame)

    def execute(self, frame):
        while frame.ip < len(frame.function.instructions):
            instruction = frame.function.instructions[frame.ip]
            frame.ip += 1

            result = self.execute_instruction(frame, instruction)

            if result is not None:
                return result

        return None

    def execute_instruction(self, frame, instruction):
        op = instruction.opcode
        args = instruction.oprands

        if op == OpCode.LOAD_CONST:
            frame.stack.append(args[0])
            return None

        if op == OpCode.LOAD_VAR:
            name = args[0]

            if name not in frame.variables:
                raise VMError(f"Undefined variable: {name}")

            frame.stack.append(frame.variables[name])
            return None

        if op == OpCode.STORE_VAR:
            name = args[0]

            if not frame.stack:
                raise VMError("Stack is empty")

            frame.variables[name] = frame.stack.pop()
            return None

        if op == OpCode.POP:
            if frame.stack:
                frame.stack.pop()
            return None

        if op == OpCode.BINARY:
            self.binary(frame, args[0])
            return None

        if op == OpCode.UNARY:
            self.unary(frame, args[0])
            return None

        if op == OpCode.JUMP:
            frame.ip = args[0]
            return None

        if op == OpCode.JUMP_IF_FALSE:
            if not frame.stack:
                raise VMError("Stack is empty")

            condition = frame.stack.pop()

            if not condition:
                frame.ip = args[0]

            return None

        if op == OpCode.CALL:
            self.call(frame, args[0], args[1])
            return None

        if op == OpCode.RETURN:
            if frame.stack:
                return frame.stack.pop()
            return None

        if op == OpCode.ITER_INIT:
            if not frame.stack:
                raise VMError("Stack is empty")

            iterable = frame.stack.pop()
            frame.iterators[args[0]] = iter(iterable)
            return None

        if op == OpCode.ITER_NEXT:
            iterator_name = args[0]
            value_name = args[1]
            has_value_name = args[2]

            iterator = frame.iterators.get(iterator_name)

            if iterator is None:
                raise VMError(f"Unknown iterator: {iterator_name}")

            try:
                value = next(iterator)
                frame.variables[value_name] = value
                frame.variables[has_value_name] = True
            except StopIteration:
                frame.variables[has_value_name] = False

            return None

        raise VMError(f"Unknown opcode: {op}")

    def binary(self, frame, operator):
        if len(frame.stack) < 2:
            raise VMError("Not enough values on stack")

        right = frame.stack.pop()
        left = frame.stack.pop()

        if operator == "ADD":
            result = left + right
        elif operator == "MINUS":
            result = left - right
        elif operator == "MULTIPLY":
            result = left * right
        elif operator == "DIVIDE":
            result = left / right
        elif operator == "MODULO":
            result = left % right
        elif operator == "GT":
            result = left > right
        elif operator == "LS":
            result = left < right
        elif operator == "GTEQ":
            result = left >= right
        elif operator == "LSEQ":
            result = left <= right
        elif operator == "EQEQ":
            result = left == right
        elif operator == "NEQ":
            result = left != right
        elif operator == "AND":
            result = bool(left) and bool(right)
        elif operator == "OR":
            result = bool(left) or bool(right)
        elif operator == "XOR":
            result = bool(left) ^ bool(right)
        else:
            raise VMError(f"Unknown binary operator: {operator}")

        frame.stack.append(result)

    def unary(self, frame, operator):
        if not frame.stack:
            raise VMError("Stack is empty")

        value = frame.stack.pop()

        if operator == "ADD":
            result = +value
        elif operator == "MINUS":
            result = -value
        elif operator == "NOT":
            result = not value
        else:
            raise VMError(f"Unknown unary operator: {operator}")

        frame.stack.append(result)

    def call(self, frame, name, arg_count):
        if len(frame.stack) < arg_count:
            raise VMError("Not enough arguments")

        args = frame.stack[-arg_count:] if arg_count else []
        if arg_count:
            del frame.stack[-arg_count:]

        if name == "output":
            for value in args:
                print(value)

            frame.stack.append(None)
            return

        if name == "input":
            value = input()
            frame.stack.append(value)
            return

        if name == "len":
            if arg_count != 1:
                raise VMError("len() takes one argument")

            frame.stack.append(len(args[0]))
            return

        if name == "range":
            frame.stack.append(range(*args))
            return

        function = None

        for current in self.call_stack[0].function.instructions:
            pass

        program_functions = getattr(self, "functions", {})
        function = program_functions.get(name)

        if function is None:
            raise VMError(f"Unknown function: {name}")

        variables = {}

        if len(args) != len(function.params):
            raise VMError(
                f"{name}() expected {len(function.params)} arguments"
            )

        for param, value in zip(function.params, args):
            variables[param] = value

        new_frame = Frame(function, variables)
        self.call_stack.append(new_frame)

        result = self.execute(new_frame)

        self.call_stack.pop()

        frame.stack.append(result)