from dataclasses import dataclass
from typing import Any
from token_type.token_type_enum import TokenType


@dataclass(frozen=True)
class Token:
    """Object that represents a token"""

    token_type: TokenType
    lexeme: str
    literal: Any
    line: int
