from typing import Callable, Dict, Any, Union, List, Optional
from src.pychart.bytecode.bytecodes import *

class BinaryEvaluator:
    evaluator: Callable[[Any, Any], Any]
    mnemonic: Mnemonics
    def __init__(self, evaluator: Callable[[Any, Any], Any], mnemonic: Mnemonics):
        self.evaluator = evaluator
        self.mnemonic = mnemonic

    def evaluate(self, interpreter, code):
        assert code.code == self.mnemonic
        result_symbol = None
        if code.destination is not None:
            interpreter.get_symbol_name_or_value(code.destination)
        left  = interpreter.get(code.left )
        right = interpreter.get(code.right)

        if isinstance(left, str) and not isinstance(right, str):
            right = str(right)
        if isinstance(right, str) and not isinstance(left, str):
            left = str(left)

        if result_symbol is not None:
            interpreter.set(result_symbol, self.evaluator(left, right))

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

class Scope:
    symbol_table: Dict[str, Any]

    def __init__(self, symbol_table: Optional[Dict[str, Any]]):
        if symbol_table is not None:
            self.symbol_table = symbol_table
        else:
            self.symbol_table = {}

    def set(self, name: str, value: Any):
        self.symbol_table[name] = value

    def get(self, name: str):
        if name in self.symbol_table:
            return self.symbol_table[name]
        return NilFlag()

    def contains(self, name: str):
        return name in self.symbol_table


class ScopeStack:
    scopes: List[Scope] = []

    def __init__(self, scopes: Optional[List[Scope]]):
        if scopes is not None:
            self.scopes = scopes
        else:
            self.scopes = []

    def __iter__(self):
        return iter(self.scopes)

    def find_missing_scopes(self, scopes: "ScopeStack"):
        missing_scopes: List[Scope] = []
        for scope in scopes:
            if scope not in self.scopes:
                missing_scopes.append(scope)
        return missing_scopes

    def get(self, name: str):
        for scope in reversed(self.scopes):
            result = scope.get(name)
            if not isinstance(result, NilFlag):
                return result
        return None

    def set(self, name: str, value: Any):
        for scope in reversed(self.scopes):
            if scope.contains(name):
                scope.set(name, value)
                return True
        return False

    def push(self, scope: Scope):
        self.scopes.append(scope)

    def pop(self):
        return self.scopes.pop()

class BytecodeInterpreter:
    # general
    def execute_create(self, code):
        assert code.code == Mnemonics.CREATE
        symbol_name = self.get_symbol_name_or_value(code.name)
        self.push(symbol_name, None)

    def execute_push(self, code):
        assert code.code in [Mnemonics.PUSH_IDENTIFIER, Mnemonics.PUSH_VALUE]
        set_value = self.get_symbol_name_or_value(code.identifier)
        get_value = self.get(code.value)
        self.push(set_value, get_value)

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

        new_stack = ScopeStack(None)
        for scope in self.scope_stack:
            new_stack.push(scope)
        new_stack.push(self.current_scope)

        fun = BytecodeInterpreterFunction(self.pc, code.arguments, new_stack)
        for arg in fun.arguments:
            fun.scope.set(self.get_symbol_name_or_value(arg), None)

        self.set(symbol_name, fun)
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
            result = fun(self, code.arguments)
            if save_result:
                self.set(addr, result)
            return None

        assert isinstance(fun, BytecodeInterpreterFunction)
        arguments = []

        for arg in code.arguments:
            arguments.append(self.get(arg))

        self.push_stack()
        missing_scopes = self.scope_stack.find_missing_scopes(fun.scope_stack)
        for scope in missing_scopes:
            self.scope_stack.push(scope)

        self.current_scope = fun.scope

        for arg in fun.arguments:
            symbol = self.get_symbol_name_or_value(arg)
            self.set(symbol, arguments.pop(0))

        result = self.execute_at(fun.address)
        for scope in missing_scopes:
            self.scope_stack.pop()
        self.pop_stack()

        if save_result:
            self.set(addr, result)

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
        self.scope_stack.push(self.current_scope)
        self.current_scope = Scope(None)

    def execute_raze(self, code):
        assert code.code == Mnemonics.RAZE
        if len(self.scope_stack.scopes) > 0:
            self.current_scope = self.scope_stack.pop()

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

    # array
    def execute_array(self, code):
        values = {}
        for (i, value) in enumerate(code.values):
            values[i] = self.get(value)

        if code.name is not None:
            symbol_name = self.get_symbol_name_or_value(code.name)
            self.set(symbol_name, values)

    def execute_array_get_at_index(self, code):
        arr = self.get(code.array)
        index = self.get(code.index)

        value = None
        if isinstance(index, float):
            if index > len(arr):
                index = None
            elif index < 0:
                if index < -len(arr):
                    index = None
                else:
                    index = len(arr) + index

        if index is not None:
            value = arr[index]

        if code.result is not None:
            symbol_name = self.get_symbol_name_or_value(code.result)
            self.set(symbol_name, value)

    def execute_array_set_at_index(self, code):
        arr_name = self.get_symbol_name_or_value(code.array)
        arr   = self.get(code.array)
        index = self.get(code.index)
        value = self.get(code.value)

        if isinstance(index, float):
            if index > len(arr):
                index = None
            elif index < 0:
                if index < -len(arr):
                    index = None
                else:
                    index = len(arr) + index

        if index is not None:
            arr[index] = value
            self.set(arr_name, arr)
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

        # array
        Mnemonics.ARRAY              : execute_array,
        Mnemonics.ARRAY_GET_AT_INDEX : execute_array_get_at_index,
        Mnemonics.ARRAY_SET_AT_INDEX : execute_array_set_at_index,
    }
    assert len(execute_byte.keys()) == len(Mnemonics)
    stack = []
    scope_stack   : ScopeStack = ScopeStack(None)
    current_scope : Scope = Scope(None)
    pc = 0
    bytecodes: List[Bytecode] = None

    def push_native(self, name, callback):
        self.current_scope.set(name, BytecodeInterpreterNativeFunction(callback))

    def push(self, name, value):
        self.current_scope.set(name, value)

    def push_stack(self):
        self.stack.append(self.pc)
        self.scope_stack.push(self.current_scope)
        self.current_scope = Scope(None)

    def pop_stack(self):
        if len(self.stack) > 0:
            self.pc = self.stack.pop()
            self.current_scope = self.scope_stack.pop()

    def get_symbol_name_or_value(self, atom: Union[Identifier, Value]):
        return atom.value

    def get(self, atom: Union[Identifier, Value]):
        assert isinstance(atom, (Identifier, Value))
        if isinstance(atom, Identifier):
            if self.current_scope.contains(atom.value):
                return self.current_scope.get(atom.value)

            value = self.scope_stack.get(atom.value)
            if isinstance(value, NilFlag):
                raise RuntimeError("unknown symbol '" + atom.value + "'")
            return value
        return atom.value

    def set(self, name: str, value: Any):
        if self.current_scope.contains(name):
            self.current_scope.set(name, value)
            return
        if not self.scope_stack.set(name, value):
            self.push(name, value)

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
    callback     : NativeCallback
    def __init__(self, callback: NativeCallback):
        self.callback = callback

    def __call__(self, interpreter: BytecodeInterpreter, args: list[Any]):
        return self.callback(interpreter, args)

class BytecodeInterpreterFunction:
    scope_stack : ScopeStack
    scope       : Scope = Scope(None)
    arguments: list[Identifier]
    address  : int
    def __init__(self, address, arguments, scope_stack: ScopeStack):
        self.arguments   = arguments
        self.address     = address
        self.scope_stack = scope_stack
