import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from src.lexer import Lexer
from src.parser import Parser

def test_let_number_location():
    source = "let x = 42;"
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()

    # The AST is a ProgramNode with a list of statements.
    # We have one statement: LetNode
    let_node = ast.statements[0]
    assert let_node.__class__.__name__ == "LetNode"
    # LetNode should point to the 'let' token
    assert let_node.line == 1
    assert let_node.col == 1  # 'l' in "let" is at column 1

    # The value of the LetNode is a NumberNode
    number_node = let_node.value
    assert number_node.__class__.__name__ == "NumberNode"
    assert number_node.value == 42
    # The number token starts at the first digit of 42, which is at column 9? Let's see:
    # "let x = 42;"
    # 123456789012345
    # l e t   x   =   4 2 ;
    # 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
    # So '4' is at column 9.
    assert number_node.line == 1
    assert number_node.col == 9

def test_identifier_location():
    source = "let x = y;"
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()

    let_node = ast.statements[0]
    assert let_node.line == 1
    assert let_node.col == 1

    # The value is an IdentifierNode for 'y'
    id_node = let_node.value
    assert id_node.__class__.__name__ == "IdentifierNode"
    assert id_node.value == "y"
    # 'y' is at column 9? Let's count:
    # "let x = y;"
    # 123456789012345
    # l e t   x   =   y ;
    # 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
    # So 'y' is at column 9.
    assert id_node.line == 1
    assert id_node.col == 9

def test_binary_expression_location():
    source = "let x = a + b;"
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()

    let_node = ast.statements[0]
    assert let_node.line == 1
    assert let_node.col == 1

    # The value is a BinaryOpNode for a + b
    bin_op = let_node.value
    assert bin_op.__class__.__name__ == "BinaryOpNode"
    assert bin_op.op == "ADD"
    # The binary expression should point to the leftmost token, which is 'a'
    assert bin_op.line == 1
    assert bin_op.col == 9  # 'a' is at column 9? Let's count:
    # "let x = a + b;"
    # 12345678901234567890
    # l e t   x   =   a   +   b ;
    # 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0
    # So 'a' is at column 9.

def test_multiline():
    source = "let x = 42\nlet y = x + 1;"
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()

    # First statement: let x = 42
    let1 = ast.statements[0]
    assert let1.line == 1
    assert let1.col == 1
    num1 = let1.value
    assert num1.line == 1
    assert num1.col == 9  # '4' in the first line

    # Second statement: let y = x + 1
    let2 = ast.statements[1]
    assert let2.line == 2
    assert let2.col == 1
    # The value is a binary op: x + 1
    bin_op = let2.value
    assert bin_op.line == 2
    assert bin_op.col == 9  # 'x' in the second line is at column 9? Let's see:
    # Line 2: "let y = x + 1;"
    # 12345678901234567890
    # l e t   y   =   x   +   1 ;
    # 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0
    # So 'x' is at column 9.

if __name__ == "__main__":
    test_let_number_location()
    test_identifier_location()
    test_binary_expression_location()
    test_multiline()
    print("All tests passed!")