from src.pychart.bytecode.bytecode import Bytecode, Mnemonics
from src.pychart.bytecode.bytecode_util import Identifier, Value, IdentifierOrValue

class UnaryBytecode(Bytecode):
    destination : Identifier
    value: IdentifierOrValue
    def __init__(self,
            mnemonic: Mnemonics,
            destination: Identifier,
            value: IdentifierOrValue,
        ):
        if not isinstance(destination, Identifier):
            raise TypeError("expected an identifier")
        if not isinstance(value, (Identifier, Value)):
            raise TypeError("expected 'left' to be an identifier or a value but got: "
                    + type(value))
        self.destination  = destination
        self.value = value

        super().__init__(mnemonic)
