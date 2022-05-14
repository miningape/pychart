from typing import Any, Dict
from src.pychart._interpreter.helpers.callable import (
    InputFunc,
    PrintFunc,
    PychartCallable,
)
from src.pychart._interpreter.native_callable.arrays import ArrayMethods
from src.pychart._interpreter.visitors.interpreter import Interpreter
from src.pychart._interpreter.visitors.resolver import Resolver
from src.pychart._interpreter.scanner import Scanner
from src.pychart._interpreter.visitors.bytecode_generator import *
from src.pychart._interpreter.pyparser import Parser
from src.pychart.bytecode.bytecodes import *
from src.pychart.bytecode.interpreter import *
from src.pychart.bytecode.printer import *

native_functions: Dict[str, PychartCallable] = {
    "input": InputFunc(),
    "print": PrintFunc(),
    "push": ArrayMethods.Push(),
    "pop": ArrayMethods.Pop(),
    "len": ArrayMethods.Length(),
}

def run_bytecode(filename: str, should_print: bool):
    source = None
    with open(filename, "r", encoding="utf-8") as contents:
        source = contents.read()

    tokens = Scanner(source).get_tokens()
    statements = Parser(tokens).parse()

    if statements is None:
        return None

    generator = BytecodeGenerator(statements, list(native_functions.keys()))
    bytecodes = generator.generate()

    if bytecodes is None:
        return None

    if should_print:
        BytecodePrinter().print(bytecodes)

    interp = BytecodeInterpreter()
    for (name, callablefn) in native_functions.items():
        interp.push(name, callablefn.bytecode_execute)
    return interp.execute(bytecodes)


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
