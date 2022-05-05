from typing import Any
from typing import Union
from typing import Optional
from enum import Enum, auto

from src.bytecode import *

class Identifier(Bytecode):
    def __init__(self, value):
        super().__init__(Mnemonics.NIL_CODE)
        self.value = value

class Literal(Bytecode):
    value : Union[int,str,float]
    def __init__(self, value):
        super().__init__(Mnemonics.NIL_CODE)
        if not union_contains(Union[int,str,float], value):
            raise TypeError("expected data but got: '" + str(value) + "'")
        self.value = value

IdentifierOrLiteral = Union[Identifier,Literal] 
def isIdentifierOrLiteral(x):
    return type(x) == Identifier or type(x) == Literal

class Label(Bytecode):
    identifier: str
    def __init__(self, identifier: str):
        super().__init__(Mnemonics.NIL_CODE)
        if type(identifier) != str:
            raise TypeError("expected a string but got: '" + str(identifier) + "'")
        self.identifier = identifier

class Noop(Bytecode):
    def __init__(self):
        super().__init__(Mnemonics.NOOP)


class Create(Bytecode):
    name: Identifier
    def __init__(self, name: Identifier):
        super().__init__(Mnemonics.CREATE)
        if type(name) != Identifier:
            raise TypeError("expected an identifier")
        self.name = name

class Push(Bytecode):
    identifier : Identifier               
    value      : IdentifierOrLiteral
    def __init__(self, identifier: Identifier, value: IdentifierOrLiteral):
        if type(identifier) != Identifier:
            raise TypeError("expected an identifier")
        self.identifier = identifier
        self.value = value

        mnemonic = None
        if type(value) == Identifier:
            mnemonic = Mnemonics.PUSH_IDENTIFIER
        elif type(value) == Literal:
            mnemonic = Mnemonics.PUSH_VALUE
        else:
            raise TypeError("expected an identifier or a value")

        super().__init__(mnemonic)


