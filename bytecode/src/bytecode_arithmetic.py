from src.bytecode import Bytecode
from src.bytecode_util import Identifier, Literal, IdentifierOrLiteral
from src.bytecode_binary import *

class Addition(BinaryBytecode):
    def __init__(self, destination: Identifier, left: IdentifierOrLiteral, right: IdentifierOrLiteral):
        super().__init__(Mnemonics.ADDITION, destination, left, right)

class Subtraction(BinaryBytecode):
    def __init__(self, destination: Identifier, left: IdentifierOrLiteral, right: IdentifierOrLiteral):
        super().__init__(Mnemonics.SUBTRACTION, destination, left, right)

class Division(BinaryBytecode):
    def __init__(self, destination: Identifier, left: IdentifierOrLiteral, right: IdentifierOrLiteral):
        super().__init__(Mnemonics.DIVISION, destination, left, right)

class Multiplication(BinaryBytecode):
    def __init__(self, destination: Identifier, left: IdentifierOrLiteral, right: IdentifierOrLiteral):
        super().__init__(Mnemonics.MULTIPLICATION, destination, left, right)
