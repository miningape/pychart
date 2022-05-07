from typing import Any, Union

from src.pychart.bytecode.bytecode import Bytecode, Mnemonics, union_contains


class Identifier(Bytecode):
    def __init__(self, value):
        super().__init__(Mnemonics.NIL_CODE)
        self.value = value

class Value(Bytecode):
    value : Union[int,str,float]
    def __init__(self, value):
        super().__init__(Mnemonics.NIL_CODE)
        if not union_contains(Union[int,str,float], value):
            raise TypeError("expected data but got: '" + str(value) + "'")
        self.value = value

IdentifierOrValue = Union[Identifier, Value]
def is_identifier_or_value(obj: Any):
    return isinstance(obj, (Identifier, Value))

class Label(Bytecode):
    identifier: str
    def __init__(self, identifier: str):
        super().__init__(Mnemonics.NIL_CODE)
        if not isinstance(identifier, str):
            raise TypeError("expected a string but got: '" + str(identifier) + "'")
        self.identifier = identifier

class Noop(Bytecode):
    def __init__(self):
        super().__init__(Mnemonics.NOOP)

class Frame(Bytecode):
    def __init__(self):
        super().__init__(Mnemonics.FRAME)

class Raze(Bytecode):
    def __init__(self):
        super().__init__(Mnemonics.RAZE)

class Create(Bytecode):
    name: Identifier
    def __init__(self, name: Identifier):
        super().__init__(Mnemonics.CREATE)
        if not isinstance(name, Identifier):
            raise TypeError("expected an identifier")
        self.name = name

class Push(Bytecode):
    identifier : Identifier
    value      : IdentifierOrValue
    def __init__(self, identifier: Identifier, value: IdentifierOrValue):
        if not isinstance(identifier, Identifier):
            raise TypeError("expected an identifier")
        self.identifier = identifier
        self.value = value

        mnemonic = None
        if isinstance(value, Identifier):
            mnemonic = Mnemonics.PUSH_IDENTIFIER
        elif isinstance(value, Value):
            mnemonic = Mnemonics.PUSH_VALUE
        else:
            raise TypeError("expected an identifier or a value")

        super().__init__(mnemonic)
