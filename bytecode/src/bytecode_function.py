
from src.bytecode import *
from src.bytecode_util import *
from src.bytecode_jumps import *

def solveBlock(bytecodes: list[Bytecode]):
    block = []
    for item in bytecodes:
        if is_list_of(Bytecode, item):
            block += item
        elif isinstance(item, Bytecode):
            block.append(item)
        else:
            raise TypeError("expected a list of bytecode but got: " + str(type(item)))
    
    labels = {}
    for i in range(len(block)):
        item = block[i]
        if type(item) == Label:
            labels[item.identifier] = i
    
    for i in range(len(block)):
        item = block[i]
        if type(item) == Jump or type(item) == JumpIfTrue:
            item.location = labels[item.location.identifier]
        elif type(item) == Label:
            block[i] = Noop()
    return block

class Function(Bytecode):
    identifier: Identifier
    arguments: list[Identifier]
    block:     list[Bytecode]
    def __init__(self, name, arguments, block):
        super().__init__(Mnemonics.FUNCTION)
        if type(name) != Identifier:
            raise TypeError("expected an identifier but got: " + str(type(name)))
        if not is_list_of(Identifier, arguments):
            raise TypeError("expected a list of identifiers but got: " + str(type(arguments)))

        self.name      = name
        self.arguments = arguments
        self.block     = solveBlock(block)

class Call(Bytecode):
    destination: Optional[Identifier]
    identifier:  Identifier
    arguments:   list[Union[Identifier, Literal]]
    def __init__(self, destination: Optional[Identifier], identifier: Identifier, arguments: list[Union[Identifier, Literal]]):
        super().__init__(Mnemonics.CALL)
        
        if destination != None and type(destination) != Identifier:
            raise TypeError("expected destination to be an identifier but got: " + str(type(destination)))
        
        if type(identifier) != Identifier:
            raise TypeError("expected identifier to be an identifier but got: " + str(type(identifier)))

        if type(arguments) != list:
            raise TypeError("expected arguments to be a list but got: " + str(type(arguments)))

        if len(arguments) > 0:
            for item in arguments:
                if not union_contains(Union[Identifier,Literal], item):
                    raise TypeError("expected a arguments to be a list identifiers and literals but got: " + str(type(item)))

        self.destination = destination
        self.identifier  = identifier
        self.arguments   = arguments

class Return(Bytecode):
    value: Optional[Union[Identifier,Literal]]
    def __init__(self, value):
        super().__init__(Mnemonics.RETURN)
        if value != None and not union_contains(Union[Identifier,Literal], value):
            raise TypeError("expected an identifier or literal but got: " + str(value))
        self.value = value
