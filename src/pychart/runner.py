from typing import Any, Dict
from src.pychart._interpreter.helpers.callable import (
    InputFunc,
    PrintFunc,
    PychartCallable,
)
from src.pychart._interpreter.visitors.interpreter import Interpreter
from src.pychart._interpreter.visitors.resolver import Resolver
from src.pychart._interpreter.scanner import Scanner
from src.pychart._interpreter.pyparser import Parser

native_functions: Dict[str, PychartCallable] = {
    "input": InputFunc(),
    "print": PrintFunc(),
}


def run(source: str):
    tokens = Scanner(source).get_tokens()
    statements = Parser(tokens).parse()

    if statements is None:
        return None

    bindings = Resolver.variable_bindings(statements, list(native_functions.keys()))
    interpreter = Interpreter(bindings)

    for (name, callablefn) in native_functions.items():
        interpreter.environment.reverve(name, callablefn)

    last_value: Any = None

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
