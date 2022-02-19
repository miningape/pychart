from typing import List
from token.exporter import Token, TokenType


class Scanner:
    # Source variables
    source: str = ""
    tokens: List[Token] = []

    # Variables to track scanner
    start: int = 0
    current: int = 0
    line: int = 1

    def __init__(self, programText: str):
        self.source = programText

    def __is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def __advance(self) -> str:
        return ""

    def __add_token(self, type: TokenType):
        pass

    def __scan_token(self):
        char = self.__advance()

        if char == "+":
            self.__add_token(TokenType.PLUS)
        elif char == "-":
            self.__add_token(TokenType.MINUS)
        elif char == "/":
            self.__add_token(TokenType.SLASH)
        elif char == "*":
            self.__add_token(TokenType.STAR)

    def get_tokens(self) -> List[Token]:
        if len(self.tokens) != 0:
            return self.tokens

      # do the tokenising
        while not self.__is_at_end():
            self.start = self.current
            self.__scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))

        return self.tokens
