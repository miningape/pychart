from src.pychart.bytecode.bytecode import Mnemonics
from src.pychart.bytecode.bytecode_util import IdentifierOrValue, Identifier
from src.pychart.bytecode.bytecode_binary import BinaryBytecode
from src.pychart.bytecode.bytecode_unary import UnaryBytecode

class Addition(BinaryBytecode):
    def __init__(self, destination: Identifier, left: IdentifierOrValue, right: IdentifierOrValue):
        super().__init__(Mnemonics.ADDITION, destination, left, right)

class Subtraction(BinaryBytecode):
    def __init__(self, destination: Identifier, left: IdentifierOrValue, right: IdentifierOrValue):
        super().__init__(Mnemonics.SUBTRACTION, destination, left, right)

class Division(BinaryBytecode):
    def __init__(self, destination: Identifier, left: IdentifierOrValue, right: IdentifierOrValue):
        super().__init__(Mnemonics.DIVISION, destination, left, right)

class Multiplication(BinaryBytecode):
    def __init__(self, destination: Identifier, left: IdentifierOrValue, right: IdentifierOrValue):
        super().__init__(Mnemonics.MULTIPLICATION, destination, left, right)

class Sign(UnaryBytecode):
    def __init__(self, destination: Identifier, value: IdentifierOrValue):
        super().__init__(Mnemonics.SIGN, destination, value)

class Negate(UnaryBytecode):
    def __init__(self, destination: Identifier, value: IdentifierOrValue):
        super().__init__(Mnemonics.NEGATE, destination, value)
