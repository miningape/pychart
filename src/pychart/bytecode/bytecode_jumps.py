from typing import Any, Union, Optional, List
from enum import Enum, auto

from src.pychart.bytecode.bytecode import *
from src.pychart.bytecode.bytecode_util import *

class Jump(Bytecode):
    location: Union[Label,int]
    def __init__(self, label: Label):
        super().__init__(Mnemonics.JUMP)
        if type(label) != Label:
            raise TypeError("expected parameter 'label' to be a label but got: '" + str(label) + "'")
        self.location = label

class JumpIfTrue(Bytecode):
    condition: Identifier
    location: Union[Label,int]
    def __init__(self, condition: Identifier, label: Label):
        super().__init__(Mnemonics.JUMP_IF_TRUE)
        if type(condition) != Identifier:
            raise TypeError("expected parameter 'condition' to be an identifier but got: '" + str(label) + "'")
        if type(label) != Label:
            raise TypeError("expected parameter 'label' to be a label but got: '" + str(label) + "'")
        self.condition = condition
        self.location = label

class JumpIfNotTrue(Bytecode):
    condition: Identifier
    location: Union[Label,int]
    def __init__(self, condition: Identifier, label: Label):
        super().__init__(Mnemonics.JUMP_IF_FALSE)
        if type(condition) != Identifier:
            raise TypeError("expected parameter 'condition' to be an identifier but got: '" + str(label) + "'")
        if type(label) != Label:
            raise TypeError("expected parameter 'label' to be a label but got: '" + str(label) + "'")
        self.condition = condition
        self.location = label

def If(name: str, condition: Identifier, true_block: list[Bytecode], false_block: list[Bytecode]) -> list[Bytecode]:
    if type(name) != str:
        raise TypeError("expected name to be a string")
    if type(condition) != Identifier:
        raise TypeError("expected parameter condition to be an identifier")
    if not is_list_of(Bytecode, true_block):
        raise TypeError("expected parameter true_block to be a list of Bytecode")
    if not is_list_of(Bytecode, false_block):
        raise TypeError("expected parameter false_block to be a list of Bytecode")

    true_label       = Label('.true_'  + name)
    end_label        = Label('.end_'   + name)
    conditional_jump = JumpIfTrue(condition, true_label)
    jump             = Jump(end_label)

    return [conditional_jump] + false_block + [jump, true_label] + true_block + [end_label]

def IfNotTrue(name: str, condition: Identifier, true_block: list[Bytecode], false_block: list[Bytecode]) -> list[Bytecode]:
    if not isinstance(name, str):
        raise TypeError("expected name to be a string")
    if not isinstance(condition, Identifier):
        raise TypeError("expected parameter condition to be an identifier")
    if not is_list_of(Bytecode, true_block):
        raise TypeError("expected parameter true_block to be a list of Bytecode")
    if not is_list_of(Bytecode, false_block):
        raise TypeError("expected parameter false_block to be a list of Bytecode")

    true_label       = Label('.true_'  + name)
    end_label        = Label('.end_'   + name)
    conditional_jump = JumpIfNotTrue(condition, true_label)
    jump             = Jump(end_label)

    return [conditional_jump] + false_block + [jump, true_label] + true_block + [end_label]


def While(name: str, header: Optional[List[Bytecode]], condition: Identifier, block: List[Bytecode]):
    if not isinstance(name, str):
        raise TypeError("expected name to be a string")
    if not isinstance(condition, Identifier):
        raise TypeError("expected parameter condition to be an identifier")
    if not is_list_of(Bytecode, block):
        raise TypeError("expected parameter block to be a list of Bytecode")

    start_label      = Label('.start_' + name)
    end_label        = Label('.end_'   + name)
    conditional_jump = JumpIfNotTrue(condition, end_label)
    jump             = Jump(start_label)

    if header is None:
        header = []

    return [start_label] + header + [conditional_jump] + block + [jump, end_label]
