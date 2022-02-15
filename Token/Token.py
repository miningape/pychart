from Token.TokenTypeEnum import TokenType
from typing import Any

class Token:
  type: TokenType
  lexeme: str
  literal: Any
  line: int

  def __init__(
    self, 
    type: TokenType,
    lexeme: str,
    literal: Any,
    line: int
    ):
    self.type = type
    self.lexeme = lexeme
    self.literal = literal
    self.line = line
  
  def __str__(self) -> str:
      return "<Token: {}, {}, {}>".format(self.type.name, self.lexeme, self.literal)