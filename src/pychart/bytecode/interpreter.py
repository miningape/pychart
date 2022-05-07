from typing import Callable
from src.pychart.bytecode.bytecodes import *

class BinaryEvaluator:
    evaluator: Callable[[Any, Any], Any]
    mnemonic: Mnemonics
    def __init__(self, evaluator: Callable[[Any, Any], Any], mnemonic: Mnemonics):
        self.evaluator = evaluator
        self.mnemonic = mnemonic

    def evaluate(self, interpreter, code):
        assert code.code == self.mnemonic
        result_symbol = interpreter.get_symbol_name_or_value(code.destination)
        left  = interpreter.get(code.left )
        right = interpreter.get(code.right)
        interpreter.current_table[result_symbol] = self.evaluator(left, right)

class UnaryEvaluator:
    evaluator: Callable[[Any], Any]
    mnemonic: Mnemonics
    def __init__(self, evaluator: Callable[[Any], Any], mnemonic: Mnemonics):
        self.evaluator = evaluator
        self.mnemonic = mnemonic

    def evaluate(self, interpreter, code):
        assert code.code == self.mnemonic
        result_symbol = interpreter.get_symbol_name_or_value(code.destination)
        value  = interpreter.get(code.value)
        interpreter.current_table[result_symbol] = self.evaluator(value)

class BytecodeInterpreter:
    # general
    def execute_create(self, code):
        assert code.code == Mnemonics.CREATE
        symbol_name = self.get_symbol_name_or_value(code.name)
        self.current_table[symbol_name] = None

    def execute_push(self, code):
        assert code.code in [Mnemonics.PUSH_IDENTIFIER, Mnemonics.PUSH_VALUE]
        set_value = self.get_symbol_name_or_value(code.identifier)
        get_value = self.get(code.value)
        self.current_table[set_value] = get_value

    # jumps
    def execute_jump(self, code):
        assert code.code == Mnemonics.JUMP
        assert isinstance(code.location, int)
        self.pc = code.location

    def execute_jump_if_true(self, code):
        assert code.code == Mnemonics.JUMP_IF_TRUE
        assert isinstance(code.location, int)
        value = self.get(code.condition)
        if value:
            self.pc = code.location

    def execute_jump_if_false(self, code):
        assert code.code == Mnemonics.JUMP_IF_FALSE
        assert isinstance(code.location, int)
        value = self.get(code.condition)
        if not value:
            self.pc = code.location

    # functions
    def execute_function(self, code):
        assert code.code == Mnemonics.FUNCTION
        symbol_name = self.get_symbol_name_or_value(code.name)
        fun = BytecodeInterpreterFunction(self.pc, code.arguments)
        for arg in fun.arguments:
            fun.symbols[self.get_symbol_name_or_value(arg)] = None

        self.current_table[symbol_name] = fun
        self.pc += code.num_instructions

    def execute_call(self, code):
        assert code.code == Mnemonics.CALL

        addr = None
        save_result = False
        if code.destination is not None:
            addr = self.get_symbol_name_or_value(code.destination)
            save_result = True

        fun = self.get(code.identifier)
        if isinstance(fun, BytecodeInterpreterNativeFunction):
            return fun(self, code.arguments)

        assert isinstance(fun, BytecodeInterpreterFunction)
        arguments = []

        for arg in code.arguments:
            arguments.append(self.get(arg))

        self.push_stack()
        self.current_table = fun.symbols

        for arg in fun.arguments:
            symbol = self.get_symbol_name_or_value(arg)
            self.current_table[symbol] = arguments.pop(0)

        result = self.execute_at(fun.address)
        self.pop_stack()

        if save_result:
            self.current_table[addr] = result

        return None

    def execute_return(self, code):
        assert code.code == Mnemonics.RETURN
        if code.value is None:
            return NilFlag()

        value = self.get(code.value)
        if value is None:
            return NilFlag()
        return value

    def execute_frame(self, code):
        assert code.code == Mnemonics.FRAME
        self.symbols.append(self.current_table)
        self.current_table = {}

    def execute_raze(self, code):
        assert code.code == Mnemonics.RAZE
        if len(self.symbols) > 0:
            self.current_table = self.symbols.pop()

    # comparisons
    equals_closure = BinaryEvaluator(lambda a, b: a == b, Mnemonics.EQUALS)
    not_equals_closure = BinaryEvaluator(lambda a, b: a != b, Mnemonics.NOT_EQUALS)
    less_than_closure = BinaryEvaluator(lambda a, b: a < b, Mnemonics.LESS_THAN)
    less_than_equals_closure = BinaryEvaluator(lambda a, b: a <= b, Mnemonics.LESS_THAN_EQUALS)
    greater_than_closure = BinaryEvaluator(lambda a, b: a > b, Mnemonics.GREATER_THAN)
    greater_than_equals_closure = BinaryEvaluator(lambda a, b: a >= b,
            Mnemonics.GREATER_THAN_EQUALS)
    logical_and_closure = BinaryEvaluator(lambda a, b: a and b, Mnemonics.LOGICAL_AND)
    logical_or_closure = BinaryEvaluator(lambda a, b: a or b, Mnemonics.LOGICAL_OR)
    logical_not_closure         = UnaryEvaluator(lambda v: not v, Mnemonics.LOGICAL_NOT)

    # arithmetic
    addition_closure       = BinaryEvaluator(lambda a, b: a + b, Mnemonics.ADDITION)
    subtraction_closure    = BinaryEvaluator(lambda a, b: a - b, Mnemonics.SUBTRACTION)
    division_closure       = BinaryEvaluator(lambda a, b: a / b, Mnemonics.DIVISION)
    multiplication_closure = BinaryEvaluator(lambda a, b: a * b, Mnemonics.MULTIPLICATION)
    sign_closure           = UnaryEvaluator(lambda v: +v, Mnemonics.SIGN)
    negate_closure         = UnaryEvaluator(lambda v: -v, Mnemonics.NEGATE)


    # -----

    execute_byte : dict[Mnemonics, Callable[[Any, Bytecode], Any] ] = {
        Mnemonics.NIL_CODE        : lambda self, code: None,
        # general
        Mnemonics.NOOP            : lambda self, code: None,
        Mnemonics.CREATE          : execute_create,
        Mnemonics.PUSH_IDENTIFIER : execute_push,
        Mnemonics.PUSH_VALUE      : execute_push,
        Mnemonics.FRAME           : execute_frame,
        Mnemonics.RAZE            : execute_raze,

        # jumps
        Mnemonics.JUMP            : execute_jump,
        Mnemonics.JUMP_IF_TRUE    : execute_jump_if_true,
        Mnemonics.JUMP_IF_FALSE   : execute_jump_if_false,

        # function
        Mnemonics.FUNCTION        : execute_function,
        Mnemonics.CALL            : execute_call,
        Mnemonics.RETURN          : execute_return,

        # comparisons
        Mnemonics.EQUALS               : equals_closure.evaluate,
        Mnemonics.NOT_EQUALS           : not_equals_closure.evaluate,
        Mnemonics.LESS_THAN            : less_than_closure.evaluate,
        Mnemonics.LESS_THAN_EQUALS     : less_than_equals_closure.evaluate,
        Mnemonics.GREATER_THAN         : greater_than_closure.evaluate,
        Mnemonics.GREATER_THAN_EQUALS  : greater_than_equals_closure.evaluate,
        Mnemonics.LOGICAL_AND          : logical_and_closure.evaluate,
        Mnemonics.LOGICAL_OR           : logical_or_closure.evaluate,
        Mnemonics.LOGICAL_NOT          : logical_not_closure.evaluate,

        # arithmetic
        Mnemonics.ADDITION       : addition_closure.evaluate,
        Mnemonics.SUBTRACTION    : subtraction_closure.evaluate,
        Mnemonics.DIVISION       : division_closure.evaluate,
        Mnemonics.MULTIPLICATION : multiplication_closure.evaluate,
        Mnemonics.SIGN           : sign_closure.evaluate,
        Mnemonics.NEGATE         : negate_closure.evaluate,
    }
    assert len(execute_byte.keys()) == len(Mnemonics)
    stack = []
    symbols = []
    current_table = {}
    pc = 0
    bytecodes: List[Bytecode] = None

    def push(self, name, callback):
        self.current_table[name] = BytecodeInterpreterNativeFunction(callback)

    def push_stack(self):
        self.stack.append(self.pc)
        self.symbols.append(self.current_table)
        self.current_table = {}

    def pop_stack(self):
        if len(self.stack) > 0:
            self.pc = self.stack.pop()
            self.current_table = self.symbols.pop()

    def get_symbol_name_or_value(self, atom: Union[Identifier, Value]):
        return atom.value

    def get(self, atom: Union[Identifier, Value]):
        assert isinstance(atom, (Identifier, Value))
        if isinstance(atom, Identifier):
            if atom.value in self.current_table:
                return self.current_table[atom.value]
            for table in reversed(self.symbols):
                if atom.value in table:
                    return table[atom.value]
            raise RuntimeError("unknown symbol '" + atom.value + "'")
        return atom.value

    def execute_at(self, address: int):
        self.pc = address + 1
        while self.pc < len(self.bytecodes):
            bt = self.bytecodes[self.pc]
            result = self.execute_byte[bt.code](self, bt)
            if result is not None:
                if isinstance(result, NilFlag):
                    return None
                return result
            self.pc = self.pc + 1
        return None

    def execute(self, bytecodes: list[Bytecode]):
        self.bytecodes = bytecodes
        self.pc = 0
        while self.pc < len(bytecodes):
            bt = bytecodes[self.pc]
            result = self.execute_byte[bt.code](self, bt)
            if result is not None:
                if isinstance(result, NilFlag):
                    return None
                return result
            self.pc = self.pc + 1
        return None

class NilFlag:
    def __init__(self):
        return

NativeCallback = Callable[[Any, BytecodeInterpreter, list[Union[Identifier, Value]]], Any]
class BytecodeInterpreterNativeFunction:
    symbols      : map
    callback     : NativeCallback
    def __init__(self, callback: NativeCallback):
        self.symbols  = {}
        self.callback = callback

    def __call__(self, interpreter: BytecodeInterpreter, args: list[Any]):
        return self.callback(interpreter, args)

class BytecodeInterpreterFunction:
    symbols  : map
    arguments: list[Identifier]
    address  : int
    def __init__(self, address, arguments):
        self.symbols = {}
        self.arguments = arguments
        self.address   = address
