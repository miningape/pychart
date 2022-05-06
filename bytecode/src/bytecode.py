from typing import Any
from typing import Union
from typing import Optional
from enum import Enum, auto

class Mnemonics(Enum):
    NIL_CODE            = 0
    # general           
    NOOP                = auto()
    CREATE              = auto()
    PUSH_IDENTIFIER     = auto()
    PUSH_VALUE          = auto()
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
    LESS_THAN           = auto()
    LESS_THAN_EQUALS    = auto()
    GREATER_THAN        = auto()
    GREATER_THAN_EQUALS = auto()
    LOGICAL_AND         = auto()
    LOGICAL_OR          = auto()

    # arithmetic
    ADDITION            = auto()
    SUBTRACTION         = auto()
    DIVISION            = auto()
    MULTIPLICATION      = auto()

def union_contains(union: Union, value: Any) -> bool:
    return isinstance(value, union.__args__)

def is_list_of(element_type: type, value: Any) -> bool:
    if type(value) != list:
        return False
    for v in value:
        if not isinstance(v, element_type):
            return False
    return True

class Bytecode:
    code : Mnemonics 
    def __init__(self, code: Mnemonics):
        self.code = code
