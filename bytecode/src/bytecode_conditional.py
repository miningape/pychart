from src.bytecode import Bytecode
from src.bytecode_util import Identifier, Literal, IdentifierOrLiteral
from src.bytecode_binary import *

class Equals(BinaryBytecode):
    def __init__(self, destination: Identifier, left: IdentifierOrLiteral, right: IdentifierOrLiteral):
        super().__init__(Mnemonics.EQUALS, destination, left, right)

class LogicalAnd(BinaryBytecode):
    def __init__(self, destination: Identifier, left: IdentifierOrLiteral, right: IdentifierOrLiteral):
        super().__init__(Mnemonics.LOGICAL_AND, destination, left, right)

class LogicalOr(BinaryBytecode):
    def __init__(self, destination: Identifier, left: IdentifierOrLiteral, right: IdentifierOrLiteral):
        super().__init__(Mnemonics.LOGICAL_OR, destination, left, right)

class LessThan(BinaryBytecode):
    def __init__(self, destination: Identifier, left: IdentifierOrLiteral, right: IdentifierOrLiteral):
        super().__init__(Mnemonics.LESS_THAN, destination, left, right)

class LessThanEquals(BinaryBytecode):
    def __init__(self, destination: Identifier, left: IdentifierOrLiteral, right: IdentifierOrLiteral):
        super().__init__(Mnemonics.LESS_THAN_EQUALS, destination, left, right)

class GreaterThan(BinaryBytecode):
    def __init__(self, destination: Identifier, left: IdentifierOrLiteral, right: IdentifierOrLiteral):
        super().__init__(Mnemonics.GREATER_THAN, destination, left, right)

class GreaterThanEquals(BinaryBytecode):
    def __init__(self, destination: Identifier, left: IdentifierOrLiteral, right: IdentifierOrLiteral):
        super().__init__(Mnemonics.GREATER_THAN_EQUALS, destination, left, right)
