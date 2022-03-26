from typing import Any, Dict, List, Union

from pkg_resources import ResolutionError
from src.pychart._interpreter.ast_nodes.expression import (
    Assignment,
    Binary,
    Call,
    Expr,
    ExprVisitor,
    Grouping,
    Literal,
    Unary,
    Variable,
)
from src.pychart._interpreter.ast_nodes.statement import (
    Block,
    Let,
    Print,
    Stmt,
    StmtVisitor,
    Expression,
)
from src.pychart._interpreter.token_type.token import Token


class Resolver(ExprVisitor, StmtVisitor):
    scopes: List[Dict[str, bool]]
    locals: Dict[Expr, int]

    def __init__(self):
        self.scopes = [{}]
        self.locals = {}

    @staticmethod
    def variable_bindings(stmts: List[Stmt], native: List[str]):
        resolver = Resolver()
        for name in native:
            resolver.scopes[0][name] = True

        resolver.resolve(stmts)

        return resolver.locals

    def resolve(
        self, thing: Union[Union[List[Stmt], List[Expr]], Union[Stmt, Expr]]
    ) -> None:
        if isinstance(thing, list):
            for ting in thing:
                self.resolve(ting)
        else:  # Else because python typing is shit
            return thing(self)

    def resolve_local(self, expr: Expr, name: Token):
        i = len(self.scopes) - 1
        while i >= 0:
            if self.scopes[i].get(name.lexeme) is not None:
                self.locals[expr] = len(self.scopes) - 1 - i
                return
            i -= 1
        raise ResolutionError(f"Variable {name} not initialised before usage")

    def open_scope(self):
        self.scopes.append({})

    def close_scope(self):
        self.scopes.pop()

    def declare(self, name: str):
        scope = self.scopes[len(self.scopes) - 1]
        scope[name] = False

    def define(self, name: str):
        scope = self.scopes[len(self.scopes) - 1]
        scope[name] = True

    # ExprVisitor
    def variable(self, expr: Variable) -> Any:
        if self.scopes[len(self.scopes) - 1].get(expr.name.lexeme) is False:
            raise ResolutionError("Cannot use variable in its own initializer.")

        self.resolve_local(expr, expr.name)
        return None

    def assignment(self, expr: Assignment) -> Any:
        self.resolve(expr.initializer)
        self.resolve_local(expr, expr.name)
        return None

    def binary(self, expr: Binary) -> Any:
        self.resolve(expr.left)
        self.resolve(expr.right)
        return None

    def unary(self, expr: Unary) -> Any:
        self.resolve(expr.right)
        return None

    def grouping(self, expr: Grouping) -> Any:
        self.resolve(expr.expr)
        return None

    def literal(self, expr: Literal) -> Any:
        return None

    def call(self, expr: Call) -> Any:
        self.resolve(expr.callee)

        for arg in expr.arguments:
            self.resolve(arg)

        return None

    # StmtVisitor
    def expression(self, stmt: Expression):
        self.resolve(stmt.expr)
        return None

    def print(self, stmt: Print):
        self.resolve(stmt.expr)

    def block(self, stmt: Block):
        self.open_scope()
        self.resolve(stmt.statements)
        self.close_scope()
        return None

    def let(self, stmt: Let):
        self.declare(stmt.name.lexeme)
        if stmt.initializer:
            self.resolve(stmt.initializer)
        self.define(stmt.name.lexeme)
        return None
