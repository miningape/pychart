from typing import List, Optional, Any

from src.pychart._interpreter.ast_nodes.expression import Expr
from src.pychart._interpreter.token_type.token import Token


class Stmt:
    def __call__(self, visitor: "StmtVisitor") -> Any:
        raise RuntimeError("Expected Stmt")


class StmtVisitor:
    @staticmethod
    def throw():
        raise Exception("Unimplemented Stmt Visitor")

    # pylint: disable=unused-argument
    def expression(self, stmt: "Expression") -> Any:
        StmtVisitor.throw()

    def print(self, stmt: "Print") -> Any:
        StmtVisitor.throw()

    def let(self, stmt: "Let") -> Any:
        StmtVisitor.throw()

    def block(self, stmt: "Block") -> Any:
        StmtVisitor.throw()

    def function(self, stmt: "Function") -> Any:
        StmtVisitor.throw()

    def if_stmt(self, stmt: "If") -> Any:
        StmtVisitor.throw()

    def while_stmt(self, stmt: "While") -> Any:
        StmtVisitor.throw()

    def break_stmt(self, stmt: "Break") -> Any:
        StmtVisitor.throw()

    # pylint: enable=unused-argument


class Expression(Stmt):
    expr: Expr

    def __init__(self, expr: Expr):
        self.expr = expr

    def __call__(self, visitor: StmtVisitor) -> Any:
        return visitor.expression(self)


class Print(Stmt):
    expr: Expr

    def __init__(self, expr: Expr):
        self.expr = expr

    def __call__(self, visitor: StmtVisitor) -> Any:
        return visitor.print(self)


class Let(Stmt):
    name: Token
    initializer: Optional[Expr]

    def __init__(self, name: Token, initializer: Optional[Expr]):
        self.name = name
        self.initializer = initializer

    def __call__(self, visitor: StmtVisitor) -> Any:
        return visitor.let(self)


class Block(Stmt):
    statements: List[Stmt]

    def __init__(self, statements: List[Stmt]):
        self.statements = statements

    def __call__(self, visitor: StmtVisitor) -> Any:
        return visitor.block(self)


class Function(Stmt):
    name: Token
    params: List[Token]
    body: List[Stmt]

    def __init__(self, name: Token, params: List[Token], body: List[Stmt]):
        self.name = name
        self.params = params
        self.body = body

    def __call__(self, visitor: StmtVisitor) -> Any:
        return visitor.function(self)


class If(Stmt):
    if_test: Expr
    if_body: Stmt
    else_body: Optional[Stmt]

    def __init__(self, if_test: Expr, if_body: Stmt, else_body: Optional[Stmt]):
        self.if_test = if_test
        self.if_body = if_body
        self.else_body = else_body

    def __call__(self, visitor: StmtVisitor) -> Any:
        return visitor.if_stmt(self)


class While(Stmt):
    while_test: Expr
    while_body: Stmt

    def __init__(self, while_test: Expr, while_body: Stmt):
        self.while_test = while_test
        self.while_body = while_body

    def __call__(self, visitor: StmtVisitor) -> Any:
        return visitor.while_stmt(self)


class Break(Stmt):
    def __init__(self):
        pass
    def __call__(self, visitor: StmtVisitor) -> Any:
        return visitor.break_stmt(self)
