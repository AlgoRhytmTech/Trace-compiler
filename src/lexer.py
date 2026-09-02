from .tokens import Token

KEYWORDS = {
    "let": "LET",
    "if": "IF",
    "elif": "ELIF",
    "else": "ELSE",
    "while": "WHILE",
    "for": "FOR",
    "return": "RETURN",
    "input": "INPUT",
    "output": "OUTPUT",
    "fxn": "FUNCTION",
    "in": "IN",
    "true":"TRUE",
    "false":"FALSE",
    "null":"NULL"

}

SINGLE_CHAR_TOKENS = {
    "+": "ADD",
    "-": "MINUS",
    "*": "MULTIPLY",
    "/": "DIVIDE",
    "%": "MODULO",
    "(": "LPAREN",
    ")": "RPAREN",
    "{": "LBRACK",
    "}": "RBRACK",
    ",": "COMMA",
    ":": "COLON",
    ";": "SEMICOLON",
    ">": "GT",
    "<": "LS",
    "&": "AND",
    "|": "OR",
    "^": "XOR",
    "!": "NOT",
    "=": "EQ"
}

DOUBLE_CHAR_TOKENS = {
    "++": "INC",
    "--": "DEC",
    "==": "EQEQ",
    "!=": "NEQ",
    ">=": "GTEQ",
    "<=": "LSEQ",
    "+=": "ADEQ",
    "-=": "MSEQ",
    "*=": "MULEQ",
    "/=": "DIVEQ",
    "%=": "MODEQ"
}

class LexerError(Exception):
    pass

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens = []

    def current_char(self):
        if self.pos >= len(self.text):
            return None
        return self.text[self.pos]

    def peek(self):
        if self.pos + 1 >= len(self.text):
            return None
        return self.text[self.pos + 1]

    def advance(self):
        ch = self.current_char()
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1

    def add_token(self, type_, value=None, line=None, col=None):
        self.tokens.append(Token(type_, value, line or self.line, col or self.col))

    def skip_whitespace(self):
        while self.current_char() is not None and self.current_char().isspace():
            self.advance()

    def skip_comment(self):
        while self.current_char() is not None and self.current_char() != "\n":
            self.advance()

    def number(self):
        start_line = self.line
        start_col = self.col
        num_str = ""
        dot_count = 0

        while self.current_char() is not None and (
            self.current_char().isdigit() or self.current_char() == "."
        ):
            if self.current_char() == ".":
                dot_count += 1
                if dot_count > 1:
                    break
            num_str += self.current_char()
            self.advance()

        if "." in num_str:
            return Token("NUMBER", float(num_str), start_line, start_col)
        return Token("NUMBER", int(num_str), start_line, start_col)

    def identifier_or_keyword(self):
        start_line = self.line
        start_col = self.col
        ident = ""

        while self.current_char() is not None and (
            self.current_char().isalnum() or self.current_char() == "_"
        ):
            ident += self.current_char()
            self.advance()

        if ident in KEYWORDS:
            return Token(KEYWORDS[ident], ident, start_line, start_col)
        return Token("IDENTIFIER", ident, start_line, start_col)

    def string(self):
        start_line = self.line
        start_col = self.col
        self.advance()
        value = ""

        while self.current_char() is not None and self.current_char() != '"':
            value += self.current_char()
            self.advance()

        if self.current_char() != '"':
            raise LexerError(f"Unterminated string at line {start_line} col {start_col}")

        self.advance()
        return Token("STRING", value, start_line, start_col)

    def tokenize(self):
        while self.current_char() is not None:
            ch = self.current_char()

            if ch.isspace():
                self.skip_whitespace()
                continue

            if ch == "#":
                self.skip_comment()
                continue

            two = ch + (self.peek() or "")
            if two in DOUBLE_CHAR_TOKENS:
                start_line = self.line
                start_col = self.col
                self.advance()
                self.advance()
                self.add_token(DOUBLE_CHAR_TOKENS[two], two, start_line, start_col)
                continue

            if ch.isdigit():
                self.tokens.append(self.number())
                continue

            if ch.isalpha() or ch == "_":
                self.tokens.append(self.identifier_or_keyword())
                continue

            if ch in SINGLE_CHAR_TOKENS:
                start_line = self.line
                start_col = self.col
                self.advance()
                self.add_token(SINGLE_CHAR_TOKENS[ch], ch, start_line, start_col)
                continue

            if ch == '"':
                self.tokens.append(self.string())
                continue

            raise LexerError(f"Unexpected character '{ch}' at line {self.line} col {self.col}")

        self.add_token("EOF", None, self.line, self.col)
        return self.tokens
