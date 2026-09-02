from .ast import *


class ParserError(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        if self.pos >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.pos]

    def advance(self):
        self.pos += 1

    def eat(self, token_kind):
        token = self.current_token()
        if token.kind != token_kind:
            raise ParserError(f"Expected {token_kind} but got {token.kind}")
        self.advance()
        return token

    def parse(self):
        statements = []
        while self.current_token().kind != "EOF":
            if self.current_token().kind == "SEMICOLON":
                self.advance()
                continue
            statements.append(self.statement())
        return ProgramNode(statements)

    def statement(self):
        token_kind = self.current_token().kind

        if token_kind == "LET":
            return self.let_statement()
        if token_kind == "OUTPUT":
            return self.output_statement()
        if token_kind == "RETURN":
            return self.return_statement()
        if token_kind == "IF":
            return self.if_statement()
        if token_kind == "WHILE":
            return self.while_statement()
        if token_kind == "FOR":
            return self.for_statement()
        if token_kind == "FUNCTION":
            return self.function_statement()

        expr = self.expr()
        if self.current_token().kind in ("EQ", "ADEQ", "MSEQ", "MULEQ", "DIVEQ", "MODEQ"):
            op = self.current_token().kind
            self.advance()
            expr = AssignNode(expr, op, self.expr(), expr.line, expr.col)
        self.optional_semicolon()
        return ExprStatementNode(expr, expr.line, expr.col)

    def let_statement(self):
        let_token = self.eat("LET")
        name_token = self.eat("IDENTIFIER")
        name = name_token.value
        value = None
        if self.current_token().kind == "EQ":
            self.advance()
            value = self.expr()
        self.optional_semicolon()
        return LetNode(name, value, let_token.line, let_token.col)

    def output_statement(self):
        output_token = self.eat("OUTPUT")
        values = self.argument_list()
        self.optional_semicolon()
        return OutputNode(values, output_token.line, output_token.col)

    def return_statement(self):
        return_token = self.eat("RETURN")
        value = None
        if self.current_token().kind not in ("SEMICOLON", "RBRACK", "EOF"):
            value = self.expr()
        self.optional_semicolon()
        return ReturnNode(value, return_token.line, return_token.col)

    def if_statement(self):
        if_token = self.eat("IF")
        condition = self.condition()
        body = self.block()
        elifs = []

        while self.current_token().kind == "ELIF":
            self.advance()
            elif_condition = self.condition()
            elif_body = self.block()
            elifs.append((elif_condition, elif_body))

        else_body = None
        if self.current_token().kind == "ELSE":
            self.advance()
            else_body = self.block()

        return IfNode(condition, body, elifs, else_body, if_token.line, if_token.col)

    def while_statement(self):
        while_token = self.eat("WHILE")
        condition = self.condition()
        body = self.block()
        return WhileNode(condition, body, while_token.line, while_token.col)

    def for_statement(self):
        for_token = self.eat("FOR")
        name_token = self.eat("IDENTIFIER")
        name = name_token.value
        self.eat("IN")
        iterable = self.expr()
        body = self.block()
        return ForNode(name, iterable, body, for_token.line, for_token.col)

    def function_statement(self):
        func_token = self.eat("FUNCTION")
        name_token = self.eat("IDENTIFIER")
        name = name_token.value
        self.eat("LPAREN")
        params = []
        if self.current_token().kind != "RPAREN":
            params.append(self.eat("IDENTIFIER").value)
            while self.current_token().kind == "COMMA":
                self.advance()
                params.append(self.eat("IDENTIFIER").value)
        self.eat("RPAREN")
        body = self.block()
        return FunctionNode(name, params, body, func_token.line, func_token.col)

    def block(self):
        l_bracket_token = self.eat("LBRACK")
        statements = []
        while self.current_token().kind not in ("RBRACK", "EOF"):
            if self.current_token().kind == "SEMICOLON":
                self.advance()
                continue
            statements.append(self.statement())
        self.eat("RBRACK")
        return BlockNode(statements, l_bracket_token.line, l_bracket_token.col)
       
        

    def condition(self):
        if self.current_token().kind == "LPAREN":
            self.advance()
            node = self.expr()
            self.eat("RPAREN")
            return node
        return self.expr()

    def argument_list(self):
        self.eat("LPAREN")
        args = []
        if self.current_token().kind != "RPAREN":
            args.append(self.expr())
            while self.current_token().kind == "COMMA":
                self.advance()
                args.append(self.expr())
        self.eat("RPAREN")
        return args

    def optional_semicolon(self):
        if self.current_token().kind == "SEMICOLON":
            self.advance()

    def expr(self):
        return self.logical_or()

    def logical_or(self):
        node = self.logical_xor()

        while self.current_token().kind == "OR":
            token = self.current_token()
            self.advance()
            right = self.logical_xor()
            node = BinaryOpNode(node, token.kind, right, node.line, node.col)

        return node

    def logical_xor(self):
        node = self.logical_and()

        while self.current_token().kind == "XOR":
            token = self.current_token()
            self.advance()
            right = self.logical_and()
            node = BinaryOpNode(node, token.kind, right, node.line, node.col)

        return node

    def logical_and(self):
        node = self.equality()

        while self.current_token().kind == "AND":
            token = self.current_token()
            self.advance()
            right = self.equality()
            node = BinaryOpNode(node, token.kind, right, node.line, node.col)

        return node

    def equality(self):
        node = self.comparison()

        while self.current_token().kind in ("EQEQ", "NEQ"):
            token = self.current_token()
            self.advance()
            right = self.comparison()
            node = BinaryOpNode(node, token.kind, right, node.line, node.col)

        return node

    def comparison(self):
        node = self.additive()

        while self.current_token().kind in ("GT", "LS", "GTEQ", "LSEQ"):
            token = self.current_token()
            self.advance()
            right = self.additive()
            node = BinaryOpNode(node, token.kind, right, node.line, node.col)

        return node

    def additive(self):
        node = self.term()

        while self.current_token().kind in ("ADD", "MINUS"):
            token = self.current_token()
            self.advance()
            right = self.term()
            node = BinaryOpNode(node, token.kind, right, node.line, node.col)

        return node

    def term(self):
        node = self.factor()

        while self.current_token().kind in ("MULTIPLY", "DIVIDE", "MODULO"):
            token = self.current_token()
            self.advance()
            right = self.factor()
            node = BinaryOpNode(node, token.kind, right, node.line, node.col)
        return node

    def factor(self):
        token = self.current_token()
        if token.kind == "INC":
            self.advance()
            operand = self.factor()
            return UnaryOpNode("PRE_INC", operand, token.line, token.col)
        if token.kind == "DEC":
            self.advance()
            operand = self.factor()
            return UnaryOpNode("PRE_DEC", operand, token.line, token.col)
        if token.kind == "ADD":
            self.advance()
            operand = self.factor()
            return UnaryOpNode("ADD", operand, token.line, token.col)
        if token.kind == "MINUS":
            self.advance()
            operand = self.factor()
            return UnaryOpNode("MINUS", operand, token.line, token.col)
        if token.kind == "NOT":
            self.advance()
            operand = self.factor()
            return UnaryOpNode("NOT", operand, token.line, token.col)
        return self.call()

    def call(self):
        node = self.primary()
        while self.current_token().kind in ("LPAREN", "INC", "DEC"):
            if self.current_token().kind == "LPAREN":
                args = self.argument_list()
                node = CallNode(node, args, node.line, node.col)
                continue
            if self.current_token().kind == "INC":
                self.advance()
                node = UnaryOpNode("POST_INC", node, node.line, node.col)
                continue
            self.advance()
            node = UnaryOpNode("POST_DEC", node, node.line, node.col)
        return node

    def primary(self):
        token = self.current_token()
        if token.kind == "NUMBER":
            self.advance()
            return NumberNode(token.value, token.line, token.col)
        if token.kind == "STRING":
            self.advance()
            return StringNode(token.value, token.line, token.col)
        if token.kind == "TRUE":
            self.advance()
            return BooleanNode(True, token.line, token.col)

        if token.kind == "FALSE":
            self.advance()
            return BooleanNode(False, token.line, token.col)
        if token.kind == "NULL":
            self.advance()
            return NullNode(token.line, token.col)
        
        if token.kind == "IDENTIFIER":
            self.advance()
            return IdentifierNode(token.value, token.line, token.col)
        if token.kind == "INPUT":
            self.advance()
            return IdentifierNode(token.value, token.line, token.col)

        if token.kind == "LPAREN":
            self.advance()
            node = self.expr()
            self.eat("RPAREN")
            return node
        raise ParserError(f"Unexpected token {token.kind}")
