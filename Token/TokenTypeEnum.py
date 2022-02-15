from enum import Enum, auto

class TokenType(Enum):
  LPeren = auto()
  RPeren = auto()

  Star = auto()
  Slash = auto()
  Plus = auto()
  Minus = auto()
  
  Number = auto()

  EOF = auto()

