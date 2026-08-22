from pathlib import Path
import argparse
from src.lexer import Lexer
from src.parser import Parser
from src.semantics import SemanticAnalyzer
from src.interpreter import Interpreter


def build_parser():
    parser = argparse.ArgumentParser(
        prog ='myc',
        description="mera apna compiler "

    )
    parser.add_argument(
        "source",
        help="source file path"
    )
    parser.add_argument(
        "-o","--output",
        help="output file path"
    )
    parser.add_argument("--tokens",
                        action="store_true",
                        help="print tokens and stop"
    )
    parser.add_argument(
        "--ast",
        action="store_true",
        help = "print ast and stop"
    )
    parser.add_argument(
        "--check",
        action ="store_true",
        help = "run semantic analysis and stop"
    )

    parser.add_argument(
        "--run",
        action = "store_true",
        help = "run program"
    )
    return parser

def main(argv = None):
    parser = build_parser()
    args = parser.parse_args(argv)

    source = Path(args.source)

    if not source.exists():
        fixed_source = Path(str(source).replace("exampels", "examples", 1))
        if "exampels" in str(source) and fixed_source.exists():
            source = fixed_source
        else:
            parser.error(f"Source file does not exist {source}")

    text = source.read_text()

    if args.output:
        output = Path(args.output)
    else:
        output = source.with_suffix(".out")


    if args.tokens:
        lexer = Lexer(text)
        tokens = lexer.tokenize()
        for token in tokens:
            print(token)
        return 0

    if args.ast:
        tokens = Lexer(text).tokenize()
        ast = Parser(tokens).parse()
        print(ast)
        return 0

    if args.check:
        tokens = Lexer(text).tokenize()
        ast = Parser(tokens).parse()
        SemanticAnalyzer().analyze(ast)
        print("Check passed")
        return 0

    if args.run:
        tokens = Lexer(text).tokenize()
        ast = Parser(tokens).parse()
        SemanticAnalyzer().analyze(ast)
        Interpreter().interpret(ast)
        return 0

    print("My compiler started")
    print(f"Source file: {source}")
    print(f"Output file: {output}")
    print("Phase 2 ready Baby")
    return 0
