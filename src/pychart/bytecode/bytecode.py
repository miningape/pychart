from typing import Any
from typing import Union
from enum import Enum, auto

class Mnemonics(Enum):
    NIL_CODE            = 0
    # general
    NOOP                = auto()
    CREATE              = auto()
    PUSH_IDENTIFIER     = auto()
    PUSH_VALUE          = auto()
    FRAME               = auto()
    RAZE                = auto()
    # jumps
    JUMP                = auto()
    JUMP_IF_TRUE        = auto()
    JUMP_IF_FALSE       = auto()
    # function
    FUNCTION            = auto()
    CALL                = auto()
    RETURN              = auto()
    # comparisons
    EQUALS              = auto()
    NOT_EQUALS          = auto()
    LESS_THAN           = auto()
    LESS_THAN_EQUALS    = auto()
    GREATER_THAN        = auto()
    GREATER_THAN_EQUALS = auto()
    LOGICAL_AND         = auto()
    LOGICAL_OR          = auto()
    LOGICAL_NOT         = auto()
    # arithmetic
    ADDITION            = auto()
    SUBTRACTION         = auto()
    DIVISION            = auto()
    MULTIPLICATION      = auto()
    SIGN                = auto()
    NEGATE              = auto()
    # array
    ARRAY               = auto()
    ARRAY_GET_AT_INDEX  = auto()
    ARRAY_SET_AT_INDEX  = auto()


def union_contains(union: Union, value: Any) -> bool:
    return isinstance(value, union.__args__)

def is_list_of(element_type: type, value: Any) -> bool:
    if not isinstance(value, list):
        return False
    for val in value:
        if not isinstance(val, element_type):
            return False
    return True

class Bytecode:
    code : Mnemonics
    def __init__(self, code: Mnemonics):
        self.code = code
