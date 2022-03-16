from distutils.errors import CompileError
from typing import Any
from src.pychart._interpreter.environment import Environment
from src.pychart._interpreter.token_type import TokenType, Token


class Expr:
    def __call__(self, environment: Environment) -> Any:
        raise RuntimeError("Empty Expresson")

    def javascript(self) -> str:
        raise CompileError("Compilation to JS - Expected instance")


def is_number(num: Any):
    typeof = type(num)
    return typeof == int or typeof == float


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

    def __call__(self, environment: Environment) -> Any:
        if self.operator.token_type == TokenType.STAR:
            return self.left(environment) * self.right(environment)
        elif self.operator.token_type == TokenType.SLASH:
            return self.left(environment) / self.right(environment)
        elif self.operator.token_type == TokenType.PLUS:
            left = self.left(environment)
            right = self.right(environment)
            state = is_number(left) == is_number(right)

            return left + right if state else str(left) + str(right)
        elif self.operator.token_type == TokenType.MINUS:
            return self.left(environment) - self.right(environment)
        elif self.operator.token_type == TokenType.GREATER_EQUAL:
            return self.left(environment) >= self.right(environment)
        elif self.operator.token_type == TokenType.GREATER:
            return self.left(environment) > self.right(environment)
        elif self.operator.token_type == TokenType.LESSER_EQUAL:
            return self.left(environment) <= self.right(environment)
        elif self.operator.token_type == TokenType.LESSER:
            return self.left(environment) < self.right(environment)
        elif self.operator.token_type == TokenType.EQUAL_EQUAL:
            return self.left(environment) == self.right(environment)
        elif self.operator.token_type == TokenType.EQUAL:
            raise RuntimeError("Not implemented.")
        elif self.operator.token_type == TokenType.BANG_EQUAL:
            return self.left(environment) != self.right(environment)

        raise RuntimeError("Call Binary Operator Undefined")

    def javascript(self) -> str:
        return (
            f"{self.right.javascript()}{self.operator.lexeme}{self.left.javascript()}"
        )


class Unary(Expr):
    operator: Token
    right: Expr

    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def __str__(self) -> str:
        return f"( {self.operator} {str(self.right)} )"

    def javascript(self) -> str:
        return f"{self.operator.lexeme}{self.right.javascript()}"

    def __call__(self, environment: Environment) -> Any:
        if self.operator.token_type == TokenType.MINUS:
            return 0 - self.right(environment)
        elif self.operator.token_type == TokenType.BANG:
            return not self.right(environment)

        raise RuntimeError("Call Unary Unefined")


class Literal(Expr):
    value: Any

    def __init__(self, value: Any):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def javascript(self) -> str:
        value = f'"{str(self.value)}"' if type(self.value) == str else self.value

        if type(value) == bool:
            if value:
                value = "true"
            else:
                value = "false"

        return str(value)

    def __call__(self, environment: Environment) -> Any:
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

    def javascript(self) -> str:
        return f"({self.expr.javascript()})"

    def __call__(self, environment: Environment) -> Any:
        return self.expr(environment)


class Variable(Expr):
    name: Token

    def __init__(self, name: Token):
        self.name = name

    @staticmethod
    def from_expr(expr: Any):
        # Probably try catch would be better should prolly test
        name = expr.name

        if name is None:
            raise RuntimeError("Cannot convert expression to variable expression")

        return Variable(name)

    def __call__(self, environment: Environment):
        return environment.retrieve(self.name.lexeme)

    def __str__(self) -> str:
        return f"(GET {self.name.lexeme})"

    def javascript(self) -> str:
        return self.name.lexeme


class Assignment(Expr):
    name: Token
    initializer: Expr

    def __init__(self, name: Token, initializer: Expr):
        self.name = name
        self.initializer = initializer

    def __call__(self, environment: Environment):
        return environment.mutate(self.name.lexeme, self.initializer(environment))

    def __str__(self) -> str:
        return f"(Assign {str(self.initializer)} to {self.name.lexeme} )"

    def javascript(self) -> str:
        return f"{self.name.lexeme}={self.initializer.javascript()}"


if __name__ == "__main__":
    # -123 * (45.67)
    expre = Binary(
        Unary(Token(TokenType.MINUS, "-", None, 1), Literal(123)),
        Token(TokenType.STAR, "*", None, 1),
        Grouping(Literal(45.67)),
    )

    print("Running expression for: -123 * (45.67)")
    print("Tree: \t", expre)
    print("Result:\t", expre(Environment()))
