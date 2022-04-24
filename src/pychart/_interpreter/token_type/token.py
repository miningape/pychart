from dataclasses import dataclass
from typing import Any
from .token_type_enum import TokenType

from re import subn


@dataclass()
class Token:
    """Object that represents a token"""

    token_type: TokenType
    lexeme: str
    literal: Any
    line: int

    def __init__(
        self, token_type: TokenType, lexeme: str, literal: Any, line: int
    ) -> None:
        self.token_type = token_type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

        if token_type is TokenType.STRING:
            # Here replacing all unescaped escape sequences with escaped sequesnce
            self.literal, _ = subn("\\\\n", "\n", str(self.literal))
