from typing import List

from .token_type import Token, TokenType
from .expression import Binary, Expr, Unary, Literal, Grouping


class Parser:
    tokens: List[Token] = []
    current: int = 0

    def __init__(self, tokens: List[Token]):
        for token, index in zip(tokens, range(len(tokens))):
            if token.token_type == TokenType.SEPARATOR:
                tokens.pop(index)

        print(tokens)
        self.tokens = tokens

    def parse(self):
        try:
            return self.expression()
        except RuntimeError:
            print("Error occurred")
            return None

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def peek(self) -> Token:
        return self.tokens[self.current]

    def is_at_end(self):
        return self.peek().token_type == TokenType.EOF

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def check(self, token: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.tokens[self.current].token_type == token

    def match(self, *tokens_to_match: TokenType) -> bool:
        for token in tokens_to_match:
            if self.check(token):
                self.advance()
                return True

        return False

    def consume(self, type_: TokenType, message: str) -> Token:
        if self.check(type_):
            return self.advance()

        self.error(self.peek(), message)

    def error(self, token: Token, message: str):
        if token.token_type == TokenType.EOF:
            print("Is at end")
        else:
            print(f"{token.line} at end. {message}")
        raise RuntimeError()

    def expression(self) -> Expr:
        return self.equality()

    def equality(self) -> Expr:
        expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()

            expr = Binary(expr, operator, right)

        return expr

    def comparison(self) -> Expr:
        expr = self.term()

        while self.match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESSER,
            TokenType.LESSER_EQUAL,
        ):
            operator = self.previous()
            right = self.term()

            expr = Binary(expr, operator, right)

        return expr

    def term(self) -> Expr:
        expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()

            expr = Binary(expr, operator, right)

        return expr

    def factor(self) -> Expr:
        expr = self.unary()

        while self.match(TokenType.STAR, TokenType.SLASH):
            operator = self.previous()
            right = self.unary()

            expr = Binary(expr, operator, right)

        return expr

    def unary(self) -> Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()

            return Unary(operator, right)

        return self.primary()

    def primary(self) -> Expr:
        if self.match(TokenType.FALSE):
            return Literal(False)
        if self.match(TokenType.TRUE):
            return Literal(True)
        if self.match(TokenType.NULL):
            return Literal(None)

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)

        if self.match(TokenType.LEFT_PEREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PEREN, "Cannot match )")
            return Grouping(expr)

        self.error(self.peek(), "Expect expression")
