from typing import Any
from src.pychart._interpreter.visitors.interpreter import Interpreter
from src.pychart._interpreter.visitors.resolver import Resolver
from src.pychart._interpreter.scanner import Scanner
from src.pychart._interpreter.pyparser import Parser

# ! Need to remove State and change calls to use visitor


def run(source: str):
    scanner = Scanner(source)
    tokens = scanner.get_tokens()
    statements = Parser(tokens).parse()
    last_value: Any = None

    if statements is None:
        return None

    bindings = Resolver.variable_bindings(statements)
    interpreter = Interpreter(bindings)

    try:
        for statement in statements:
            last_value = statement(interpreter)
    except Exception as err:
        print(f"Error: {err}")
        print("Exiting...")

    return last_value


def run_prompt():
    try:
        while True:
            line = input("$ : ")

            if line == ".exit":
                break

            result = run(line)
            if result:
                print(result)

    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        exit()


def run_file(filename: str):
    with open(filename, "r", encoding="utf-8") as contents:
        run(contents.read())
