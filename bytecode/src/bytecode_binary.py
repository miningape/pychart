from src.bytecode import Bytecode, Mnemonics
from src.bytecode_util import Identifier, Literal, IdentifierOrLiteral

class BinaryBytecode(Bytecode):
    destination : Identifier
    left : IdentifierOrLiteral
    right: IdentifierOrLiteral
    def __init__(self, mnemonic: Mnemonics, destination: Identifier, left: IdentifierOrLiteral, right: IdentifierOrLiteral):
        if type(destination) != Identifier:
            raise TypeError("expected an identifier")
        if not(type(left) == Identifier or type(left) == Literal):
            raise TypeError("expected 'left' to be an identifier or a value but got: " + type(left))
        if not(type(right) == Identifier or type(right) == Literal):
            raise TypeError("expected 'right' to be an identifier or a value but got: " + type(right))
        self.destination  = destination
        self.left  = left 
        self.right = right

        super().__init__(mnemonic)

