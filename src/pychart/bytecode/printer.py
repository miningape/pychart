from typing import Dict, Callable, Any

from src.pychart.bytecode.bytecodes import *

def demangle(name):
    while name.startswith(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.')):
        name = name[1:]
    return name

def identifier_or_value_to_string(obj):
    if isinstance(obj, Identifier):
        return demangle(obj.value)
    if isinstance(obj.value, str):
        return '"' + obj.value + '"'
    return str(obj.value)

class BytecodePrinter:
    function_len = 0
    counter = 0

    def common(self, i, code, alternative_bytecode: Optional[str] = None):
        out = ''
        if self.function_len != 0:
            out += '\t'
            self.counter += 1
            self.function_len -= 1
        elif self.counter != 0:
            out += '\n'
            self.counter = 0
        out += str(i).rjust(2) + ':\t'
        if alternative_bytecode is not None:
            out += alternative_bytecode
        else:
            out += code.code.name.lower()
        out += '\t'
        return out

    def label_print(self, code):
        out = ''
        if self.function_len != 0:
            out += '\t'
            self.counter += 1
            self.function_len -= 1
        elif self.counter != 0:
            out += '\n'
            self.counter = 0
        out += code.identifier + ':\t'
        print(out)

    def generic_print(self, i, code):
        if isinstance(code, Label):
            self.label_print(code)
        else:
            print(self.common(i, code))


    def create_print(self, i, code):
        out = self.common(i, code)
        out += demangle(code.name.value)
        print(out)

    def push_print(self, i, code):
        out = self.common(i, code, alternative_bytecode='push')

        out += demangle(code.identifier.value) + ', '
        out += identifier_or_value_to_string(code.value)
        print(out)

    def return_print(self, i, code):
        out = self.common(i, code)

        if code.value is not None:
            out += identifier_or_value_to_string(code.value)
        else:
            out += 'None'
        print(out)

    binary_name_map : Dict[Bytecode, str] = {
        Addition         : 'add',
        Subtraction      : 'sub',
        Division         : 'div',
        Multiplication   : 'mul',
        Equals           : 'eq',
        NotEquals        : 'neq',
        LessThan         : 'lt',
        LessThanEquals   : 'lte',
        GreaterThan      : 'gt',
        GreaterThanEquals: 'gte',
        LogicalAnd       : 'and',
        LogicalOr        : 'or',
    }

    def binary_print(self, i, code):
        name = self.binary_name_map[type(code)]
        out = self.common(i, code, alternative_bytecode=name)

        if code.destination is not None:
            out += identifier_or_value_to_string(code.destination)
        else:
            out += 'None'
        out += ', '

        out += identifier_or_value_to_string(code.left)
        out += ', '
        out += identifier_or_value_to_string(code.right)
        print(out)

    def unary_print(self, i, code):
        name = None
        if isinstance(code, LogicalNot):
            name = 'not'
        if code.destination is not None:
            out += identifier_or_value_to_string(code.destination)
        else:
            out += 'None'

        out += ', '

        out += identifier_or_value_to_string(code.value)
        print(out)

    def function_print(self, i, code):
        out = self.common(i, code, alternative_bytecode='func')
        out += demangle(code.name.value)
        self.function_len = code.num_instructions
        self.counter = 0
        print (out)

    def jump_print(self, i, code):
        name = None
        if isinstance(code, JumpIfTrue):
            name = 'jnez'
        elif isinstance(code, JumpIfNotTrue):
            name = 'jeqz'
        out = self.common(i, code, alternative_bytecode=name)

        if isinstance(code, (JumpIfTrue, JumpIfNotTrue)):
            out += demangle(code.condition.value) + ',\t'
        if isinstance(code.location, Label):
            out += code.location.identifier
        else:
            out += str(code.location)
        print(out)

    def call_print(self, i, code):
        out = self.common(i, code)

        if code.destination is not None:
            out += identifier_or_value_to_string(code.destination)
        else:
            out += 'None'

        out += ', '
        out += identifier_or_value_to_string(code.identifier)
        out += ', ['
        for arg in code.arguments:
            out += identifier_or_value_to_string(arg)
            if code.arguments.index(arg) != len(code.arguments) - 1:
                out += ', '
        out += ']'
        print(out)
    
    def array_print(self, i, code):
        out = self.common(i, code)

        if code.name is not None:
            out += identifier_or_value_to_string(code.name)
        else:
            out += 'None'

        out += ', ['
        for arg in code.values:
            out += identifier_or_value_to_string(arg)
            if code.values.index(arg) != len(code.values) - 1:
                out += ', '
        out += ']'
        print(out)

    def array_get_print(self, i, code):
        out = self.common(i, code, alternative_bytecode='arrget')

        if code.result is not None:
            out += identifier_or_value_to_string(code.result)
        else:
            out += 'None'
        out += ', '

        out += identifier_or_value_to_string(code.array)
        out += ', '

        out += identifier_or_value_to_string(code.index)
        print(out)

    def array_set_print(self, i, code):
        out = self.common(i, code, alternative_bytecode='arrset')

        out += identifier_or_value_to_string(code.array)
        out += ', '

        out += identifier_or_value_to_string(code.index)
        out += ', '

        out += identifier_or_value_to_string(code.value)
        print(out)

    print_byte : Dict[Mnemonics, Callable[[Any, Bytecode], Any]] = {
        Mnemonics.NIL_CODE        : generic_print,
        # general
        Mnemonics.NOOP            : generic_print,
        Mnemonics.CREATE          : create_print,
        Mnemonics.PUSH_IDENTIFIER : push_print,
        Mnemonics.PUSH_VALUE      : push_print,
        Mnemonics.FRAME           : generic_print,
        Mnemonics.RAZE            : generic_print,

        # jumps
        Mnemonics.JUMP            : jump_print,
        Mnemonics.JUMP_IF_TRUE    : jump_print,
        Mnemonics.JUMP_IF_FALSE   : jump_print,

        # function
        Mnemonics.FUNCTION        : function_print,
        Mnemonics.CALL            : call_print,
        Mnemonics.RETURN          : return_print,

        # comparisons
        Mnemonics.EQUALS               : binary_print,
        Mnemonics.NOT_EQUALS           : binary_print,
        Mnemonics.LESS_THAN            : binary_print,
        Mnemonics.LESS_THAN_EQUALS     : binary_print,
        Mnemonics.GREATER_THAN         : binary_print,
        Mnemonics.GREATER_THAN_EQUALS  : binary_print,
        Mnemonics.LOGICAL_AND          : binary_print,
        Mnemonics.LOGICAL_OR           : binary_print,
        Mnemonics.LOGICAL_NOT          : unary_print,

        # arithmetic
        Mnemonics.ADDITION       : binary_print,
        Mnemonics.SUBTRACTION    : binary_print,
        Mnemonics.DIVISION       : binary_print,
        Mnemonics.MULTIPLICATION : binary_print,
        Mnemonics.SIGN           : unary_print,
        Mnemonics.NEGATE         : unary_print,

        # array
        Mnemonics.ARRAY              : array_print,
        Mnemonics.ARRAY_GET_AT_INDEX : array_get_print,
        Mnemonics.ARRAY_SET_AT_INDEX : array_set_print,
    }
    assert len(print_byte.keys()) == len(Mnemonics)

    def print(self, bytecodes: List[Bytecode]):
        for (i, code) in enumerate(bytecodes):
            self.print_byte[code.code](self, i, code)
