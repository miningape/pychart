from typing import Any, Optional, Dict

from src.pychart._interpreter.helpers.environment import Environment
from src.pychart._interpreter.token_type import TokenType, Token


class Expr:
    def __call__(self, state: "State") -> Any:
        raise RuntimeError("Empty Expresson")

    def visit(self, visitor: "ExprVisitor") -> Any:
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


class State:
    environment: Environment = Environment()
    resolution_map: Dict["Expr", int] = {}

    def __init__(self, enclosing: Optional["State"] = None):
        if enclosing:
            self.environment = Environment(enclosing.environment)
            self.resolution_map = enclosing.resolution_map

    def set_resolution_map(self, resolution_map: Dict[Expr, int]):
        self.resolution_map = resolution_map


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

    def visit(self, visitor: ExprVisitor):
        return visitor.binary(self)

    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def __str__(self) -> str:
        return f"( {self.operator} {str(self.left)}, {str(self.right)} )"

    def __call__(self, state: State) -> Any:
        if self.operator.token_type == TokenType.STAR:
            return self.left(state) * self.right(state)
        elif self.operator.token_type == TokenType.SLASH:
            return self.left(state) / self.right(state)
        elif self.operator.token_type == TokenType.PLUS:
            left = self.left(state)
            right = self.right(state)
            state = is_number(left) == is_number(right)

            return left + right if state else str(left) + str(right)
        elif self.operator.token_type == TokenType.MINUS:
            return self.left(state) - self.right(state)
        elif self.operator.token_type == TokenType.GREATER_EQUAL:
            return self.left(state) >= self.right(state)
        elif self.operator.token_type == TokenType.GREATER:
            return self.left(state) > self.right(state)
        elif self.operator.token_type == TokenType.LESSER_EQUAL:
            return self.left(state) <= self.right(state)
        elif self.operator.token_type == TokenType.LESSER:
            return self.left(state) < self.right(state)
        elif self.operator.token_type == TokenType.EQUAL_EQUAL:
            return self.left(state) == self.right(state)
        elif self.operator.token_type == TokenType.EQUAL:
            raise RuntimeError("Not implemented.")
        elif self.operator.token_type == TokenType.BANG_EQUAL:
            return self.left(state) != self.right(state)

        raise RuntimeError("Call Binary Operator Undefined")


class Unary(Expr):
    operator: Token
    right: Expr

    def visit(self, visitor: ExprVisitor):
        return visitor.unary(self)

    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def __str__(self) -> str:
        return f"( {self.operator} {str(self.right)} )"

    def __call__(self, state: State) -> Any:
        if self.operator.token_type == TokenType.MINUS:
            return 0 - self.right(state)
        elif self.operator.token_type == TokenType.BANG:
            return not self.right(state)

        raise RuntimeError("Call Unary Unefined")


class Literal(Expr):
    value: Any

    def visit(self, visitor: ExprVisitor):
        return visitor.literal(self)

    def __init__(self, value: Any):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def __call__(self, state: State) -> Any:
        return try_cast_int(self.value)


class Grouping(Expr):
    expr: Expr

    def visit(self, visitor: ExprVisitor):
        return visitor.grouping(self)

    def __init__(self, expr_: Expr):
        self.expr = expr_

    def __str__(self) -> str:
        return f"( {str(self.expr)} )"

    def __call__(self, state: State) -> Any:
        return self.expr(state)


class Variable(Expr):
    name: Token

    def visit(self, visitor: "ExprVisitor"):
        return visitor.variable(self)

    def __init__(self, name: Token):
        self.name = name

    @staticmethod
    def from_expr(expr: Any):
        name = expr.name

        if name is None:
            raise RuntimeError("Cannot convert expression to variable expression")

        return Variable(name)

    def __call__(self, state: State):
        return state.environment.retrieve(self.name.lexeme)


class Assignment(Expr):
    name: Token
    initializer: Expr

    def visit(self, visitor: "ExprVisitor"):
        return visitor.assignment(self)

    def __init__(self, name: Token, initializer: Expr):
        self.name = name
        self.initializer = initializer

    def __call__(self, state: State):
        return state.environment.mutate(self.name.lexeme, self.initializer(state))


if __name__ == "__main__":
    # -123 * (45.67)
    expre = Binary(
        Unary(Token(TokenType.MINUS, "-", None, 1), Literal(123)),
        Token(TokenType.STAR, "*", None, 1),
        Grouping(Literal(45.67)),
    )

    print("Running expression for: -123 * (45.67)")
    print("Tree: \t", expre)
    print("Result:\t", expre(State()))
