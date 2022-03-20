from typing import Any, Dict, List
from .token_type import Token, TokenType


class Scanner:
    """Scanner class handles turning source text into a list of tokens

    Parameters:
        program_text: str - The source text to turn into tokens

    Methods:
        get_tokens() -> List[Token] - Turns the source text used into a list of tokens
    """

    # Source variables
    source: str = ""
    tokens: List[Token] = []

    # Variables to track scanner
    start: int = 0
    current: int = 0
    line: int = 1

    keywords: Dict[str, TokenType] = {
        "if": TokenType.IF,
        "else": TokenType.ELSE,
        "elif": TokenType.ELIF,
        "func": TokenType.FUNCTION,
        "return": TokenType.RETURN,
        "while": TokenType.WHILE,
        "null": TokenType.NULL,
        "let": TokenType.LET,
        "false": TokenType.FALSE,
        "true": TokenType.TRUE,
        "print": TokenType.PRINT,
    }

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

    def __match(self, char: str) -> bool:
        if self.__is_at_end():
            return False

        if char != self.source[self.current]:
            return False

        self.current += 1
        return True

    def __peek(self) -> str:
        if self.__is_at_end():
            return "\0"
        return self.source[self.current]

    def __peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"

        return self.source[self.current + 1]

    def __string(self):
        while self.__peek() != '"' and not self.__is_at_end():
            if self.__peek() == "\n":
                self.line += 1
            self.__advance()

        if self.__is_at_end():
            pass  # Throw error -> string not ended

        self.__advance()

        value = self.source[self.start + 1 : self.current - 1]
        self.__add_token(TokenType.STRING, value)

    def __number(self):
        while self.__peek().isdigit():
            self.__advance()

        if self.__peek() == "." and self.__peek_next().isdigit():
            self.__advance()
            while self.__peek().isdigit():
                self.__advance()

        self.__add_token(
            TokenType.NUMBER, float(self.source[self.start : self.current])
        )

    def __identifier(self):
        while self.__peek().isalnum():
            self.__advance()

        text = self.source[self.start : self.current]

        type_of = self.keywords.get(text)
        if type_of is None:
            type_of = TokenType.IDENTIFIER

        self.__add_token(type_of)

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

        # 1 or 2 char tokens
        elif char == "!":
            self.__add_token(
                TokenType.BANG_EQUAL if self.__match("=") else TokenType.BANG
            )
        elif char == "=":
            self.__add_token(
                TokenType.EQUAL_EQUAL if self.__match("=") else TokenType.EQUAL
            )
        elif char == ">":
            self.__add_token(
                TokenType.GREATER_EQUAL if self.__match("=") else TokenType.GREATER
            )
        elif char == "<":
            self.__add_token(
                TokenType.LESSER_EQUAL if self.__match("=") else TokenType.LESSER
            )

        # Comments
        elif char == "/":
            if self.__match("/"):
                while self.__peek() != "\n" and not self.__is_at_end():
                    self.__advance()
            else:
                self.__add_token(TokenType.SLASH)

        # Whitespace
        elif char == " " or char == "\r" or char == "\t":
            # Ignore whitespace
            pass
        elif char == "\n":
            self.line += 1

        # Literals
        elif char == '"':
            self.__string()
        elif char.isdigit():
            self.__number()
        elif char.isalpha():
            self.__identifier()
        else:
            pass  # Throw error -> unrecognised token

    def get_tokens(self) -> List[Token]:
        if len(self.tokens) != 0:
            self.tokens = []

        # do the tokenising
        while not self.__is_at_end():
            self.start = self.current
            self.__scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))

        return self.tokens
