from typing import Any
from .token_type import TokenType, Token


class Expr:
    def __call__(self) -> Any:
        raise RuntimeError("Empty Expresson")


class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def __str__(self) -> str:
        return f"( {self.operator} {str(self.left)}, {str(self.right)} )"

    def __call__(self) -> Any:
        if self.operator.token_type == TokenType.STAR:
            return self.left() * self.right()
        elif self.operator.token_type == TokenType.SLASH:
            return self.left() / self.right()
        elif self.operator.token_type == TokenType.PLUS:
            left = self.left()
            right = self.right()
            state = type(left) == type(right)

            return left + right if state else str(left) + str(right)
        elif self.operator.token_type == TokenType.MINUS:
            return self.left() - self.right()
        elif self.operator.token_type == TokenType.GREATER_EQUAL:
            return self.left() >= self.right()
        elif self.operator.token_type == TokenType.GREATER:
            return self.left() > self.right()
        elif self.operator.token_type == TokenType.LESSER_EQUAL:
            return self.left() <= self.right()
        elif self.operator.token_type == TokenType.LESSER:
            return self.left() < self.right()
        elif self.operator.token_type == TokenType.EQUAL_EQUAL:
            return self.left() == self.right()
        elif self.operator.token_type == TokenType.EQUAL:
            raise RuntimeError("Not implemented.")
        elif self.operator.token_type == TokenType.BANG_EQUAL:
            return self.left() != self.right()

        raise RuntimeError("Call Binary Operator Undefined")


class Unary(Expr):
    operator: Token
    right: Expr

    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def __str__(self) -> str:
        return f"( {self.operator} {str(self.right)} )"

    def __call__(self) -> Any:
        if self.operator.token_type == TokenType.MINUS:
            return 0 - self.right()
        elif self.operator.token_type == TokenType.BANG:
            return not self.right()

        raise RuntimeError("Call Unary Unefined")


class Literal(Expr):
    value: Any

    def __init__(self, value: Any):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def __call__(self) -> Any:
        return try_cast_int(self.value)


def try_cast_int(num: Any):
    if isinstance(num, (float)):
        if int(num) == num:
            return int(num)

    return num


class Grouping(Expr):
    expr: Expr

    def __init__(self, expr_: Expr):
        self.expr = expr_

    def __str__(self) -> str:
        return f"( {str(self.expr)} )"

    def __call__(self) -> Any:
        return self.expr()


if __name__ == "__main__":
    # -123 * (45.67)
    expr = Binary(
        Unary(Token(TokenType.MINUS, "-", None, 1), Literal(123)),
        Token(TokenType.STAR, "*", None, 1),
        Grouping(Literal(45.67)),
    )

    print("Running expression for: -123 * (45.67)")
    print("Tree: \t", expr)
    print("Result:\t", expr())
