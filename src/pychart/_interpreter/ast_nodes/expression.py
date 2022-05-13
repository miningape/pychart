from typing import Any, List

from src.pychart._interpreter.token_type import Token


class Expr:
    def __call__(self, visitor: "ExprVisitor") -> Any:
        raise RuntimeError("Expected Expr")


class ExprVisitor:
    @staticmethod
    def throw():
        raise Exception("Unimplemented Expr Visitor")

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

    def call(self, expr: "Call") -> Any:
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

    def __call__(self, visitor: ExprVisitor) -> Any:
        return visitor.binary(self)


class Unary(Expr):
    operator: Token
    right: Expr

    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def __call__(self, visitor: ExprVisitor) -> Any:
        return visitor.unary(self)


class Literal(Expr):
    value: Any

    def __init__(self, value: Any):
        self.value = value

    def __call__(self, visitor: ExprVisitor) -> Any:
        return visitor.literal(self)


class Grouping(Expr):
    expr: Expr

    def __init__(self, expr: Expr):
        self.expr = expr

    def __call__(self, visitor: ExprVisitor) -> Any:
        return visitor.grouping(self)


class Variable(Expr):
    name: Token

    def __init__(self, name: Token):
        self.name = name

    def __call__(self, visitor: ExprVisitor) -> Any:
        return visitor.variable(self)


class Assignment(Expr):
    name: Token
    initializer: Expr

    def __init__(self, name: Token, initializer: Expr):
        self.name = name
        self.initializer = initializer

    def __call__(self, visitor: ExprVisitor) -> Any:
        return visitor.assignment(self)


class Call(Expr):
    callee: Expr
    arguments: List[Expr]

    def __init__(self, callee: Expr, arguments: List[Expr]):
        self.callee = callee
        self.arguments = arguments

    def __call__(self, visitor: ExprVisitor) -> Any:
        return visitor.call(self)
