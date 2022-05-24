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

class BytecodeArrayNatives:
    def push(self, interpreter: Any, params: List[Any]):
        arr_name = interpreter.get_symbol_name_or_value(params[0])
        arr   = interpreter.get(params[0])
        value = interpreter.get(params[1])

        arr[len(arr)] = value
        interpreter.set(arr_name, arr)

    def pop(self, interpreter: Any, params: List[Any]):
        arr_name = interpreter.get_symbol_name_or_value(params[0])
        arr   = interpreter.get(params[0])

        arr.pop(len(arr) - 1, None)
        interpreter.set(arr_name, arr)

    def length(self, interpreter: Any, params: List[Any]):
        arr   = interpreter.get(params[0])
        return len(arr)



def run_bytecode(filename: str, should_print: bool):
    source = None
    with open(filename, "r", encoding="utf-8") as contents:
        source = contents.read()

    tokens = Scanner(source).get_tokens()
    statements = Parser(tokens).parse()

    if statements is None:
        return None

    generator = BytecodeGenerator(statements, list(native_functions.keys()))
    bytecodes = generator.generate(keep_labels=should_print)

    if bytecodes is None:
        return None

    if should_print:
        BytecodePrinter().print(bytecodes)
        print()
        bytecodes = solve_block(bytecodes)

    interp = BytecodeInterpreter()

    interp.push_native("input", InputFunc().bytecode_execute)
    interp.push_native("print", PrintFunc().bytecode_execute)

    array_natives = BytecodeArrayNatives()
    interp.push_native("push", array_natives.push)
    interp.push_native("pop", array_natives.pop)
    interp.push_native("len", array_natives.length)

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
        print("\nKeyboard Interrupted")
        exit()
        
    except EOFError:
        print()
        exit()


def run_file(filename: str):
    with open(filename, "r", encoding="utf-8") as contents:
        run(contents.read())
