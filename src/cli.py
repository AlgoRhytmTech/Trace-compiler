import argparse

from src.lexer import Lexer
from src.parser import Parser
from src.semantics import SemanticAnalyzer
from src.codegen import TraceIRLowerer
from src.bytecode_compiler import BytecodeCompiler
from src.vm import VM


VERSION = "0.1.0"


def build_parser():
    parser = argparse.ArgumentParser(
        prog="trace",
        description="TRACE - Translational Runtime Analysis and Compilation Engine"
    )

    parser.add_argument(
        "file",
        nargs="?",
        help="TRACE source file (.trc)"
    )

    parser.add_argument(
        "--run",
        action="store_true",
        help="Run the TRACE program"
    )

    parser.add_argument(
        "--tokens",
        action="store_true",
        help="Show lexer tokens"
    )

    parser.add_argument(
        "--ast",
        action="store_true",
        help="Show parsed AST"
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Run semantic analysis"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"TRACE {VERSION}"
    )

    return parser


def compile_source(filename):
    with open(filename, "r") as file:
        source = file.read()

    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()

    analyzer = SemanticAnalyzer(filename)
    diagnostics = analyzer.analyze(ast)

    return source, tokens, ast, diagnostics


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.file:
        parser.print_help()
        return 0

    try:
        source, tokens, ast, diagnostics = compile_source(args.file)
    except FileNotFoundError:
        print(f"trace: file not found: {args.file}")
        return 1
    except Exception as e:
        print(f"trace: {e}")
        return 1

    if args.tokens:
        for token in tokens:
            print(token)
        return 0

    if args.ast:
        print(ast)
        return 0

    if args.check:
        if diagnostics.has_error:
            diagnostics.print_all()
            return 1

        print("Check passed")
        return 0

    if diagnostics.has_error:
        diagnostics.print_all()
        return 1

    ir = TraceIRLowerer().lower(ast)
    bytecode = BytecodeCompiler().compile(ir)

    VM().run(bytecode)

    return 0


if __name__ == "__main__":
    main()