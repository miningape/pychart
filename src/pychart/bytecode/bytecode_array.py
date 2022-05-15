from typing import List, Optional

from src.pychart.bytecode.bytecode import (Bytecode, Mnemonics, is_list_of)
from src.pychart.bytecode.bytecode_util import (Identifier, IdentifierOrValue, Value)

class Array(Bytecode):
    name  : Identifier
    values: List[IdentifierOrValue]

    def __init__(self, name: Identifier, values: List[IdentifierOrValue]):
        super().__init__(Mnemonics.ARRAY)
        if not isinstance(name, Identifier):
            raise TypeError("expected an identifier but got: " + str(type(name)))
        if not isinstance(values, List):
            raise TypeError("expected a list of identifiers but got: " + str(type(values)))

        for val in values:
            if not isinstance(val, (Identifier, Value)):
                raise TypeError("expected a list of identifiers but got: " + str(type(val)))

        self.name   = name
        self.values = values

class ArrayGetAtIndex(Bytecode):
    result : Optional[Identifier]
    array  : Identifier
    index  : IdentifierOrValue
    def __init__(self, result: Optional[Identifier], array: Identifier, index: IdentifierOrValue):
        super().__init__(Mnemonics.ARRAY_GET_AT_INDEX)
        if result is not None and not isinstance(result, Identifier):
            raise TypeError("expected an identifier but got: " + str(type(result)))
        if not isinstance(array, Identifier):
            raise TypeError("expected an identifier but got: " + str(type(array)))
        if not isinstance(index, (Identifier, Value)):
            raise TypeError("expected an identifier or a value but got: " + str(type(index)))

        self.result = result
        self.array  = array
        self.index  = index

class ArraySetAtIndex(Bytecode):
    array : Identifier
    index : IdentifierOrValue
    value : IdentifierOrValue
    def __init__(self, array: Identifier, index: IdentifierOrValue, value: IdentifierOrValue):
        super().__init__(Mnemonics.ARRAY_SET_AT_INDEX)
        if not isinstance(array, Identifier):
            raise TypeError("expected an identifier but got: " + str(type(array)))
        if not isinstance(index, (Identifier, Value)):
            raise TypeError("expected an identifier but got: " + str(type(index)))
        if not isinstance(value, (Identifier, Value)):
            raise TypeError("expected an identifier or a value but got: " + str(type(value)))

        self.array = array
        self.index = index
        self.value = value
