from audioop import add
from time import time
from typing import Any, Dict
from src.pychart._interpreter.helpers.callable import (
    InputFunc,
    PrintFunc,
    PychartCallable,
)
from src.pychart._interpreter.visitors.compiler import (
    Compiler,
    VMState,
    run_virtual_machine,
)
from src.pychart._interpreter.native_callable.arrays import ArrayMethods
from src.pychart._interpreter.visitors.interpreter import Interpreter
from src.pychart._interpreter.visitors.resolver import Resolver
from src.pychart._interpreter.scanner import Scanner
from src.pychart._interpreter.pyparser import Parser

native_functions: Dict[str, PychartCallable] = {
    "input": InputFunc(),
    "print": PrintFunc(),
    "push": ArrayMethods.Push(),
    "pop": ArrayMethods.Pop(),
    "len": ArrayMethods.Length(),
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
        start = time()
        for statement in statements:
            last_value = statement(interpreter)
        print(time() - start)
    except Exception as err:
        print(f"Error: {err}")
        print("Exiting...")

    return last_value


def compilation(source: str):
    tokens = Scanner(source).get_tokens()
    statements = Parser(tokens).parse()

    if statements is None:
        return None

    bindings = Resolver.variable_bindings(statements, list(native_functions.keys()))
    compiler = Compiler(bindings)

    start = time()
    for statement in statements:
        statement(compiler)

    # print("--- PROGRAM ---")
    # for i, cmd in enumerate(compiler.commandQueue):
    #     print(i, cmd)

    # print()
    # print("--- OUTPUT ---")

    vm_state = VMState(compiler.commandQueue)
    run_virtual_machine(vm_state)
    print(time() - start)


def compile_file(filename: str):
    with open(filename, "r", encoding="utf-8") as contents:
        compilation(contents.read())


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
