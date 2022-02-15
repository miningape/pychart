from re import S
from typing import List
from Token.exporter import Token, TokenType


class Scanner:
  # Source variables
  source: str
  tokens: List[Token]

  # Variables to track scanner
  start: int = 0
  current: int = 0
  line: int = 1

  def __init__(self, programText: str):
    self.source = programText

  def __isAtEnd(self) -> bool:
    return self.current >= len(self.source)

  def __advance() -> str:
    return ""

  def __add_token(self, type: TokenType):
    pass

  def __scan_token(self):
    char = self.__advance()

    if char == "+":
      self.__add_token(TokenType.Plus)
    elif char == "-":
      self.__add_token(TokenType.Minus)
    elif char == "/":
      self.__add_token(TokenType.Slash)
    elif char == "*":
      self.__add_token(TokenType.Star)

  def getTokens(self) -> List[Token]:
    if len(self.tokens) != 0:
      return self.tokens

    # do the tokenising
    while not self.__isAtEnd():
      self.start = self.current
      self.__scan_token()

    self.tokens.append(Token(TokenType.EOF, "", None, self.line))

    return self.tokens
