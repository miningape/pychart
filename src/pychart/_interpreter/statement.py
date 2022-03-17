from typing import List, Optional, Any
from src.pychart._interpreter.environment import Environment
from src.pychart._interpreter.expression import Expr, Token


class Stmt:
    def __call__(self, environment: Environment) -> Any:
        raise RuntimeError("Expected Actual Statement")


class Expression(Stmt):
    expr: Expr

    def __init__(self, expr: Expr):
        self.expr = expr

    def __call__(self, environment: Environment):
        return self.expr(environment)


class Print(Stmt):
    expr: Expr

    def __init__(self, expr: Expr):
        self.expr = expr

    def __call__(self, environment: Environment):
        print(self.expr(environment))
        return None


class Let(Stmt):
    name: Token
    initializer: Optional[Expr]

    def __init__(self, name: Token, initializer: Optional[Expr]):
        self.name = name
        self.initializer = initializer

    def __call__(self, environment: Environment):
        value = None
        if self.initializer is not None:
            value = self.initializer(environment)

        environment.reverve(self.name.lexeme, value)
        return value


class Block(Stmt):
    statements: List[Stmt]

    def __init__(self, statements: List[Stmt]):
        self.statements = statements

    def __call__(self, environment: Environment):
        environment = Environment(environment)

        for statement in self.statements:
            statement(environment)


class If(Stmt):
    if_test: Expr
    if_body: Stmt
    else_body: Optional[Stmt]

    def __init__(
        self,
        if_test: Expr,
        if_body: Stmt,
        else_body: Optional[Stmt],
    ):
        self.if_test = if_test
        self.if_body = if_body

        self.else_body = else_body

    def __call__(self, environment: Environment):
        test_result = self.if_test(environment)
        if test_result:
            self.if_body(environment)
        elif self.else_body and not test_result:
            self.else_body(environment)
