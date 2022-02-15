from typing import List
from Token.exporter import Token, TokenType

def tokenize(programText: str) -> List[Token]:
  print(programText)
  return []

if __name__ == "__main__":
  print("Starting ruc#")
  x = Token(TokenType.LPeren, "oi", None, 1)
  print(x)

  

  