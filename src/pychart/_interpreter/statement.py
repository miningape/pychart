from typing import List, Optional, Any
from src.pychart._interpreter.environment import Environment
from src.pychart._interpreter.expression import Expr, Token


class Stmt:
    def __call__(self, environment: Environment) -> Any:
        raise RuntimeError("Expected Actual Statement")

    def visit(self, visitor: "StmtVisitor") -> Any:
        raise RuntimeError("Unimplmented visitor visit")


class StmtVisitor:
    @staticmethod
    def throw():
        raise Exception("Unimplmented visitor method")

    # pylint: disable=unused-argument
    def expression(self, stmt: "Expression") -> Any:
        StmtVisitor.throw()

    def print(self, stmt: "Print") -> Any:
        StmtVisitor.throw()

    def let(self, stmt: "Let") -> Any:
        StmtVisitor.throw()

    def block(self, stmt: "Block") -> Any:
        StmtVisitor.throw()

    # pylint: enable=unused-argument


class Expression(Stmt):
    expr: Expr

    def visit(self, visitor: "StmtVisitor"):
        return visitor.expression(self)

    def __init__(self, expr: Expr):
        self.expr = expr

    def __call__(self, environment: Environment):
        return self.expr(environment)


class Print(Stmt):
    expr: Expr

    def visit(self, visitor: "StmtVisitor") -> Any:
        return visitor.print(self)

    def __init__(self, expr: Expr):
        self.expr = expr

    def __call__(self, environment: Environment):
        print(self.expr(environment))
        return None


class Let(Stmt):
    name: Token
    initializer: Optional[Expr]

    def visit(self, visitor: "StmtVisitor") -> Any:
        return visitor.let(self)

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

    def visit(self, visitor: "StmtVisitor") -> Any:
        return visitor.block(self)

    def __init__(self, statements: List[Stmt]):
        self.statements = statements

    def __call__(self, environment: Environment):
        environment = Environment(environment)

        for statement in self.statements:
            statement(environment)
