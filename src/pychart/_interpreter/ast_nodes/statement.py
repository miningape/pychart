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

    def return_stmt(self, stmt: "Return") -> Any:
        StmtVisitor.throw()

    def let(self, stmt: "Let") -> Any:
        StmtVisitor.throw()

    def block(self, stmt: "Block") -> Any:
        StmtVisitor.throw()

    def function(self, stmt: "Function") -> Any:
        StmtVisitor.throw()

    def if_stmt(self, stmt: "If") -> Any:
        StmtVisitor.throw()

    # pylint: enable=unused-argument


class Expression(Stmt):
    expr: Expr

    def __init__(self, expr: Expr):
        self.expr = expr

    def __call__(self, visitor: StmtVisitor) -> Any:
        return visitor.expression(self)


class Return(Stmt):
    expr: Expr

    def __init__(self, expr: Expr):
        self.expr = expr

    def __call__(self, visitor: StmtVisitor) -> Any:
        return visitor.return_stmt(self)


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
