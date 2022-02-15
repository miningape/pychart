from typing import List
from Token.exporter import Token


class Scanner:
  source: str
  tokens: List[Token]

  def __init__(self, programText: str):
    self.source = programText
  
  def getTokens(self) -> List[Token]:
    if len(self.tokens) != 0:
      return self.tokens

    # do the tokenising

    return self.tokens 