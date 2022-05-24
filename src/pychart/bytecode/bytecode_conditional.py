
from src.pychart.bytecode.bytecode import Mnemonics
from src.pychart.bytecode.bytecode_util import IdentifierOrValue, Identifier
from src.pychart.bytecode.bytecode_binary import BinaryBytecode
from src.pychart.bytecode.bytecode_unary import UnaryBytecode

class Equals(BinaryBytecode):
    def __init__(self, destination: Identifier, left: IdentifierOrValue, right: IdentifierOrValue):
        super().__init__(Mnemonics.EQUALS, destination, left, right)

class NotEquals(BinaryBytecode):
    def __init__(self, destination: Identifier, left: IdentifierOrValue, right: IdentifierOrValue):
        super().__init__(Mnemonics.NOT_EQUALS, destination, left, right)

class LessThan(BinaryBytecode):
    def __init__(self, destination: Identifier, left: IdentifierOrValue, right: IdentifierOrValue):
        super().__init__(Mnemonics.LESS_THAN, destination, left, right)

class LessThanEquals(BinaryBytecode):
    def __init__(self, destination: Identifier, left: IdentifierOrValue, right: IdentifierOrValue):
        super().__init__(Mnemonics.LESS_THAN_EQUALS, destination, left, right)

class GreaterThan(BinaryBytecode):
    def __init__(self, destination: Identifier, left: IdentifierOrValue, right: IdentifierOrValue):
        super().__init__(Mnemonics.GREATER_THAN, destination, left, right)

class GreaterThanEquals(BinaryBytecode):
    def __init__(self, destination: Identifier, left: IdentifierOrValue, right: IdentifierOrValue):
        super().__init__(Mnemonics.GREATER_THAN_EQUALS, destination, left, right)

class LogicalAnd(BinaryBytecode):
    def __init__(self, destination: Identifier, left: IdentifierOrValue, right: IdentifierOrValue):
        super().__init__(Mnemonics.LOGICAL_AND, destination, left, right)

class LogicalOr(BinaryBytecode):
    def __init__(self, destination: Identifier, left: IdentifierOrValue, right: IdentifierOrValue):
        super().__init__(Mnemonics.LOGICAL_OR, destination, left, right)

class LogicalNot(UnaryBytecode):
    def __init__(self, destination: Identifier, value: IdentifierOrValue):
        super().__init__(Mnemonics.LOGICAL_NOT, destination, value)
