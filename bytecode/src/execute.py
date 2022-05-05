from typing import Callable
from src.bytecodes import *

class BinaryEvaluator:
    evaluator: Callable[[Any, Any], Any]
    mnemonic: Mnemonics
    def __init__(self, evaluator: Callable[[Any, Any], Any], mnemonic: Mnemonics):
        self.evaluator = evaluator
        self.mnemonic = mnemonic

    def evaluate(self, executor, code):
        assert code.code == self.mnemonic
        result_symbol = executor.getSymbolNameOrValue(code.destination)
        left  = executor.get(code.left )
        right = executor.get(code.right)
        executor.current_table[result_symbol] = self.evaluator(left, right)
        return

class Executor:
    # general 
    def execute_create(self, code):
        assert code.code == Mnemonics.CREATE
        symbol_name = self.getSymbolNameOrValue(code.name)
        self.current_table[symbol_name] = None
        return
    
    def execute_push(self, code):
        assert code.code == Mnemonics.PUSH_IDENTIFIER or code.code == Mnemonics.PUSH_VALUE
        set_value = self.getSymbolNameOrValue(code.identifier)
        get_value = self.get(code.value)
        self.current_table[set_value] = get_value

    # jumps
    def execute_jump(self, code):
        assert code.code == Mnemonics.JUMP
        assert type(code.location) == int
        self.pc = code.location
        return

    def execute_jump_if_true(self, code):
        assert code.code == Mnemonics.JUMP_IF_TRUE
        assert type(code.location) == int
        value = self.get(code.condition)
        if value:
            self.pc = code.location
        return

    def execute_jump_if_false(self, code):
        assert code.code == Mnemonics.JUMP_IF_FALSE
        assert type(code.location) == int
        value = self.get(code.condition)
        if not value:
            self.pc = code.location
        return

    # functions
    def execute_function(self, code):
        assert code.code == Mnemonics.FUNCTION
        symbol_name = self.getSymbolNameOrValue(code.name)
        fun = ExecutorFunction(code.arguments, code.block)
        for arg in fun.arguments:
            fun.symbols[self.getSymbolNameOrValue(arg)] = None

        self.current_table[symbol_name] = fun
        return

    
    def execute_call(self, code):
        assert code.code == Mnemonics.CALL

        addr = None
        save_result = False
        if code.destination != None:
            addr = self.getSymbolNameOrValue(code.destination)
            save_result = True

        fun = self.get(code.identifier)
        if type(fun) == ExecutorNativeFunction:
            return fun.callback(fun.userdata, self, code.arguments)
        
        assert type(fun) == ExecutorFunction
        arguments = []

        for arg in code.arguments:
            arguments.append(self.get(arg))

        self.push_stack()
        self.current_table = fun.symbols

        for arg in fun.arguments:
            symbol = self.getSymbolNameOrValue(arg)
            self.current_table[symbol] = arguments.pop(0)

        result = self.execute(fun.instructions)
        self.pop_stack()
        if save_result:
            self.current_table[addr] = result
        return

    def execute_return(self, code):
        assert code.code == Mnemonics.RETURN
        if code.value == None:
            return NilFlag()

        value = self.get(code.value)
        if value == None:
            return NilFlag()
        else:
            return value
    # comparisons
    equals_closure = BinaryEvaluator(lambda a, b: a == b, Mnemonics.EQUALS)
    logical_and_closure = BinaryEvaluator(lambda a, b: a and b, Mnemonics.LOGICAL_AND)
    logical_or_closure = BinaryEvaluator(lambda a, b: a or b, Mnemonics.LOGICAL_OR)
    less_than_closure = BinaryEvaluator(lambda a, b: a < b, Mnemonics.LESS_THAN)
    less_than_equals_closure = BinaryEvaluator(lambda a, b: a <= b, Mnemonics.LESS_THAN_EQUALS)
    greater_than_closure = BinaryEvaluator(lambda a, b: a > b, Mnemonics.GREATER_THAN)
    greater_than_equals_closure = BinaryEvaluator(lambda a, b: a >= b, Mnemonics.GREATER_THAN_EQUALS)

    # arithmetic
    addition_closure       = BinaryEvaluator(lambda a, b: a + b, Mnemonics.ADDITION)
    subtraction_closure    = BinaryEvaluator(lambda a, b: a - b, Mnemonics.SUBTRACTION)
    division_closure       = BinaryEvaluator(lambda a, b: a / b, Mnemonics.DIVISION)
    multiplication_closure = BinaryEvaluator(lambda a, b: a * b, Mnemonics.MULTIPLICATION)

    # -----

    execute_byte : dict[Mnemonics, Callable[[Any, Bytecode], Any] ] = {
        Mnemonics.NIL_CODE        : lambda self, code: None,
        # general 
        Mnemonics.NOOP            : lambda self, code: None,
        Mnemonics.CREATE          : execute_create,
        Mnemonics.PUSH_IDENTIFIER : execute_push,
        Mnemonics.PUSH_VALUE      : execute_push,

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
        Mnemonics.LESS_THAN            : less_than_closure.evaluate,
        Mnemonics.LESS_THAN_EQUALS     : less_than_equals_closure.evaluate,
        Mnemonics.GREATER_THAN         : greater_than_closure.evaluate,
        Mnemonics.GREATER_THAN_EQUALS  : greater_than_equals_closure.evaluate,
        Mnemonics.LOGICAL_AND          : logical_and_closure.evaluate,
        Mnemonics.LOGICAL_OR           : logical_or_closure.evaluate,

        # arithmetic
        Mnemonics.ADDITION       : addition_closure.evaluate,
        Mnemonics.SUBTRACTION    : subtraction_closure.evaluate,
        Mnemonics.DIVISION       : division_closure.evaluate,
        Mnemonics.MULTIPLICATION : multiplication_closure.evaluate,
    }
    assert len(execute_byte.keys()) == len(Mnemonics)
    stack = []
    symbols = []
    current_table = {}
    pc = 0

    def push(self, name, userdata, callback, num_args='*'):
        self.current_table[name] = ExecutorNativeFunction(userdata, callback, num_args=num_args)

    def push_stack(self):
        self.stack.append(self.pc)
        self.symbols.append(self.current_table)
        self.current_table = {}
    
    def pop_stack(self):
        self.pc = self.stack.pop()
        self.current_table = self.symbols.pop()

    def getSymbolNameOrValue(self, atom: Union[Identifier, Literal]):
        return atom.value

    def get(self, atom: Union[Identifier, Literal]):
        assert type(atom) == Identifier or type(atom) == Literal
        if type(atom) == Identifier:
            if atom.value in self.current_table:
                return self.current_table[atom.value]
            else:
                for table in reversed(self.symbols):
                    if atom.value in table:
                        return table[atom.value]
            raise RuntimeError("unknown symbol '" + atom.value + "'")
        else:
            return atom.value

    def execute(self, bytecodes: list[Bytecode]):
        self.pc = 0
        while self.pc < len(bytecodes):
            bt = bytecodes[self.pc]
            result = self.execute_byte[bt.code](self, bt)
            if result != None:
                if type(result) == NilFlag:
                    return None
                else:
                    return result
            self.pc = self.pc + 1
        return None

class NilFlag:
    def __init__(self): 
        return

NativeCallback = Callable[[Any, Executor, list[Union[Identifier, Literal]]], Any]
class ExecutorNativeFunction:
    symbols      : map
    userdata     : Any
    num_args     : int
    callback     : NativeCallback
    def __init__(self, userdata: Any, callback: NativeCallback, num_args: Union[int, str] = '*'):
        self.symbols  = {}
        self.userdata = userdata
        self.num_args = num_args
        self.callback = callback

class ExecutorFunction: 
    symbols      : map
    instructions : list[Bytecode]
    arguments    : list[Identifier]
    def __init__(self, arguments, instructions):
        self.symbols = {}
        self.arguments = arguments
        self.instructions = instructions

