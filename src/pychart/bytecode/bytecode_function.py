
from typing import List, Optional, Union

# god i hate formatters
from src.pychart.bytecode.bytecode import (Bytecode, Mnemonics, is_list_of,
                                           union_contains)
from src.pychart.bytecode.bytecode_jumps import Jump, JumpIfTrue
from src.pychart.bytecode.bytecode_util import (Frame, Identifier,
                                                IdentifierOrValue, Label, Noop,
                                                Value)


def solve_block(bytecodes: list[Bytecode]):
    block = []
    for item in bytecodes:
        if is_list_of(Bytecode, item):
            block += item
        elif isinstance(item, Bytecode):
            block.append(item)
        else:
            raise TypeError("expected a list of bytecode but got: " + str(type(item)))

    labels = {}
    for (i, item) in enumerate(block):
        if isinstance(item, Label):
            labels[item.identifier] = i

    for (i, item) in enumerate(block):
        if isinstance(item, (Jump, JumpIfTrue)):
            item.location = labels[item.location.identifier]
        elif isinstance(item, Label):
            block[i] = Noop()
    return block

class Function(Bytecode):
    name: Identifier
    arguments: List[Identifier]
    num_instructions: int
    def __init__(self, name, arguments, num_instructions):
        super().__init__(Mnemonics.FUNCTION)
        if not isinstance(name, Identifier):
            raise TypeError("expected an identifier but got: " + str(type(name)))
        if not is_list_of(Identifier, arguments):
            raise TypeError("expected a list of identifiers but got: " + str(type(arguments)))

        self.name             = name
        self.arguments        = arguments
        self.num_instructions = num_instructions

class Call(Bytecode):
    destination: Optional[Identifier]
    identifier:  Identifier
    arguments:   List[IdentifierOrValue]
    def __init__(self,
            destination: Optional[Identifier],
            identifier: Identifier,
            arguments: list[Union[Identifier, Value]]
        ):
        super().__init__(Mnemonics.CALL)

        if destination is not None and not isinstance(destination, Identifier):
            raise TypeError("expected destination to be an identifier but got: "
                    + str(type(destination)))

        if not isinstance(identifier, Identifier):
            raise TypeError("expected identifier to be an identifier but got: "
                    + str(type(identifier)))

        if not isinstance(arguments, list):
            raise TypeError("expected arguments to be a list but got: " + str(type(arguments)))

        if len(arguments) > 0:
            for item in arguments:
                if not union_contains(Union[Identifier,Value], item):
                    raise TypeError(
                            "expected a arguments to be a list identifiers and literals but got: "
                            + str(type(item)))

        self.destination = destination
        self.identifier  = identifier
        self.arguments   = arguments

class Return(Bytecode):
    value: Optional[Union[Identifier,Value]]
    def __init__(self, value):
        super().__init__(Mnemonics.RETURN)
        if value is not None and not union_contains(Union[Identifier,Value], value):
            raise TypeError("expected an identifier or literal but got: " + str(value))
        self.value = value
