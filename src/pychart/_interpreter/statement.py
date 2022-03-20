from typing import List, Optional, Any
from src.pychart._interpreter.environment import Environment
from src.pychart._interpreter.expression import Expr, Token
from src.pychart._interpreter.token_type.token_type_enum import TokenType


class Stmt:
    def __call__(self, environment: Environment) -> Any:
        raise RuntimeError("Expected Actual Statement")

    def visit(self, stmt: "StmtVisitor"):
        raise RuntimeError("Unimplmented visitor visit")


class StmtVisitor:
    @staticmethod
    def throw():
        raise Exception("Unimplmented visitor method")

    def expression(self, stmt: "Expression"):
        StmtVisitor.throw()

    def print(self, stmt: "Print"):
        StmtVisitor.throw()

    def let(self, stmt: "Let"):
        StmtVisitor.throw()


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
