import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from src.lexer import Lexer
from src.parser import Parser

def test_let_number_location():
    source = "let x = 42;"
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()

  
    let_node = ast.statements[0]
    assert let_node.__class__.__name__ == "LetNode"
 
    assert let_node.line == 1
    assert let_node.col == 1  

   
    number_node = let_node.value
    assert number_node.__class__.__name__ == "NumberNode"
    assert number_node.value == 42
    
    assert number_node.line == 1
    assert number_node.col == 9

def test_identifier_location():
    source = "let x = y;"
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()

    let_node = ast.statements[0]
    assert let_node.line == 1
    assert let_node.col == 1

  
    id_node = let_node.value
    assert id_node.__class__.__name__ == "IdentifierNode"
    assert id_node.value == "y"
  
    assert id_node.line == 1
    assert id_node.col == 9

def test_binary_expression_location():
    source = "let x = a + b;"
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()

    let_node = ast.statements[0]
    assert let_node.line == 1
    assert let_node.col == 1


    bin_op = let_node.value
    assert bin_op.__class__.__name__ == "BinaryOpNode"
    assert bin_op.op == "ADD"
   
    assert bin_op.line == 1
    assert bin_op.col == 9  


def test_multiline():
    source = "let x = 42\nlet y = x + 1;"
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()

 
    let1 = ast.statements[0]
    assert let1.line == 1
    assert let1.col == 1
    num1 = let1.value
    assert num1.line == 1
    assert num1.col == 9  

    let2 = ast.statements[1]
    assert let2.line == 2
    assert let2.col == 1

    bin_op = let2.value
    assert bin_op.line == 2
    assert bin_op.col == 9 

if __name__ == "__main__":
    test_let_number_location()
    test_identifier_location()
    test_binary_expression_location()
    test_multiline()
    print("All tests passed!")
