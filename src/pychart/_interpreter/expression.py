from typing import Any
from src.pychart._interpreter.environment import Environment
from src.pychart._interpreter.token_type import TokenType, Token


class Expr:
    def __call__(self, environment: Environment) -> Any:
        raise RuntimeError("Empty Expresson")

    def accept(self, visitor: "ExprVisitor"):
        raise RuntimeError("resolve unimplemented for expr")


class ExprVisitor:
    @staticmethod
    def throw():
        raise Exception("Unimplemented expr visitor")

    # pylint: disable=unused-argument
    def binary(self, expr: "Binary") -> Any:
        ExprVisitor.throw()

    def unary(self, expr: "Unary") -> Any:
        ExprVisitor.throw()

    def literal(self, expr: "Literal") -> Any:
        ExprVisitor.throw()

    def grouping(self, expr: "Grouping") -> Any:
        ExprVisitor.throw()

    def variable(self, expr: "Variable") -> Any:
        ExprVisitor.throw()

    def assignment(self, expr: "Assignment") -> Any:
        ExprVisitor.throw()

    # pylint: enable=unused-argument


def is_number(num: Any):
    typeof = type(num)
    return typeof == int or typeof == float


def try_cast_int(num: Any):
    if isinstance(num, (float)):
        if int(num) == num:
            return int(num)

    return num


class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: ExprVisitor):
        return visitor.binary(self)

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


class Unary(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor: ExprVisitor):
        return visitor.unary(self)

    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def __str__(self) -> str:
        return f"( {self.operator} {str(self.right)} )"

    def __call__(self, environment: Environment) -> Any:
        if self.operator.token_type == TokenType.MINUS:
            return 0 - self.right(environment)
        elif self.operator.token_type == TokenType.BANG:
            return not self.right(environment)

        raise RuntimeError("Call Unary Unefined")


class Literal(Expr):
    value: Any

    def accept(self, visitor: ExprVisitor):
        return visitor.literal(self)

    def __init__(self, value: Any):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def __call__(self, environment: Environment) -> Any:
        return try_cast_int(self.value)


class Grouping(Expr):
    expr: Expr

    def accept(self, visitor: ExprVisitor):
        return visitor.grouping(self)

    def __init__(self, expr_: Expr):
        self.expr = expr_

    def __str__(self) -> str:
        return f"( {str(self.expr)} )"

    def __call__(self, environment: Environment) -> Any:
        return self.expr(environment)


class Variable(Expr):
    name: Token

    def accept(self, visitor: "ExprVisitor"):
        return visitor.variable(self)

    def __init__(self, name: Token):
        self.name = name

    @staticmethod
    def from_expr(expr: Any):
        name = expr.name

        if name is None:
            raise RuntimeError("Cannot convert expression to variable expression")

        return Variable(name)

    def __call__(self, environment: Environment):
        return environment.retrieve(self.name.lexeme)


class Assignment(Expr):
    name: Token
    initializer: Expr

    def accept(self, visitor: "ExprVisitor"):
        return visitor.assignment(self)

    def __init__(self, name: Token, initializer: Expr):
        self.name = name
        self.initializer = initializer

    def __call__(self, environment: Environment):
        return environment.mutate(self.name.lexeme, self.initializer(environment))


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
