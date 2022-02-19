from enum import Enum, auto

# pylint: disable=multiple-statements
class TokenType(Enum):
    # Brackets
    LEFT_PEREN = auto(); RIGHT_PEREN = auto()
    LEFT_BRACE = auto(); RIGHT_BRACE = auto()

    # Punctuation
    COMMA = auto(); DOT = auto(); SEMICOLON = auto()

    # Operators
    STAR = auto(); SLASH = auto(); PLUS = auto(); MINUS = auto()

    # Boolean Operators
    BANG = auto(); BANG_EQUAL = auto()
    EQUAL = auto(); EQUAL_EQUAL = auto()
    GREATER = auto(); GREATER_EQUAL = auto()
    LESSER = auto(); LESSER_EQUAL = auto()

    # Literals
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()

    # Keywords
    TRUE = auto()
    FALSE = auto()
    NULL = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FUNCTION = auto()
    RETURN = auto()
    PRINT = auto()

    EOF = auto()
# pylint: enable=multiple-statements
