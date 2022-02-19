from typing import Any
from token.token_type_enum import TokenType

class Token:
    token_type: TokenType
    lexeme: str
    literal: Any
    line: int

    def __init__(
        self,
        token_type: TokenType,
        lexeme: str,
        literal: Any,
        line: int
    ):
        self.token_type = token_type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self) -> str:
        return f"<Token: {self.token_type.name}, {self.lexeme}, {self.literal}>"