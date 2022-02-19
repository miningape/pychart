from typing import Any, List
from token.exporter import Token, TokenType


class Scanner:
    # Source variables
    source: str = ""
    tokens: List[Token] = []

    # Variables to track scanner
    start: int = 0
    current: int = 0
    line: int = 1

    def __init__(self, program_text: str):
        self.source = program_text

    def __is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def __advance(self) -> str:
        char = self.source[self.current]
        self.current += 1
        return char

    def __add_token(self, token_type: TokenType, literal: Any = None):
        text = self.source[self.start : self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))

    def __scan_token(self):
        char = self.__advance()

        # Single char tokens
        if char == "+":
            self.__add_token(TokenType.PLUS)
        elif char == "-":
            self.__add_token(TokenType.MINUS)
        elif char == "*":
            self.__add_token(TokenType.STAR)
        elif char == "{":
            self.__add_token(TokenType.LEFT_BRACE)
        elif char == "}":
            self.__add_token(TokenType.RIGHT_BRACE)
        elif char == "(":
            self.__add_token(TokenType.LEFT_PEREN)
        elif char == ")":
            self.__add_token(TokenType.RIGHT_PEREN)
        elif char == ",":
            self.__add_token(TokenType.COMMA)
        elif char == ".":
            self.__add_token(TokenType.DOT)
        elif char == ";":
            self.__add_token(TokenType.SEMICOLON)

    def get_tokens(self) -> List[Token]:
        if len(self.tokens) != 0:
            self.tokens = []

        # do the tokenising
        while not self.__is_at_end():
            self.start = self.current
            self.__scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))

        return self.tokens
