from src.pychart.bytecode.bytecode import Bytecode, Mnemonics
from src.pychart.bytecode.bytecode_util import Identifier, Value, IdentifierOrValue
from typing import Optional

class BinaryBytecode(Bytecode):
    destination : Optional[Identifier]
    left : IdentifierOrValue
    right: IdentifierOrValue
    def __init__(self,
            mnemonic: Mnemonics,
            destination: Optional[Identifier],
            left: IdentifierOrValue,
            right: IdentifierOrValue
        ):
        if destination is not None and not isinstance(destination, Identifier):
            raise TypeError("expected an identifier")
        if not isinstance(left, (Identifier, Value)):
            raise TypeError("expected 'left' to be an identifier or a value but got: "
                    + type(left))
        if not isinstance(right, (Identifier, Value)):
            raise TypeError("expected 'right' to be an identifier or a value but got: "
                    + type(right))
        self.destination = destination
        self.left  = left
        self.right = right

        super().__init__(mnemonic)
