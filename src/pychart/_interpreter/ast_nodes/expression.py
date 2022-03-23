from typing import Any
from src.pychart._interpreter.token_type import TokenType, Token


class Expr:
    def __call__(self, visitor: "ExprVisitor") -> Any:
        raise RuntimeError("Empty Expresson")


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

    def __call__(self, visitor: "ExprVisitor") -> Any:
        return visitor.binary(self)


class Unary(Expr):
    operator: Token
    right: Expr

    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def __str__(self) -> str:
        return f"( {self.operator} {str(self.right)} )"

    def __call__(self, visitor: "ExprVisitor") -> Any:
        return visitor.unary(self)


class Literal(Expr):
    value: Any

    def __init__(self, value: Any):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def __call__(self, visitor: ExprVisitor) -> Any:
        return visitor.literal(self)


class Grouping(Expr):
    expr: Expr

    def __init__(self, expr_: Expr):
        self.expr = expr_

    def __str__(self) -> str:
        return f"( {str(self.expr)} )"

    def __call__(self, visitor: ExprVisitor) -> Any:
        return visitor.grouping(self)


class Variable(Expr):
    name: Token

    def __init__(self, name: Token):
        self.name = name

    @staticmethod
    def from_expr(expr: Any):
        name = expr.name

        if name is None:
            raise RuntimeError("Cannot convert expression to variable expression")

        return Variable(name)

    def __call__(self, visitor: ExprVisitor):
        return visitor.variable(self)


class Assignment(Expr):
    name: Token
    initializer: Expr

    def __init__(self, name: Token, initializer: Expr):
        self.name = name
        self.initializer = initializer

    def __call__(self, visitor: ExprVisitor):
        return visitor.assignment(self)


if __name__ == "__main__":
    # -123 * (45.67)
    expre = Binary(
        Unary(Token(TokenType.MINUS, "-", None, 1), Literal(123)),
        Token(TokenType.STAR, "*", None, 1),
        Grouping(Literal(45.67)),
    )

    print("Running expression for: -123 * (45.67)")
    print("Tree: \t", expre)
    print("Result:\t")
