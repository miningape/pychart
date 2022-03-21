from typing import Any, Dict, List, Union

from pkg_resources import ResolutionError
from src.pychart._interpreter.ast_nodes.expression import Expr, ExprVisitor, Variable
from src.pychart._interpreter.ast_nodes.statement import Block, Let, Stmt, StmtVisitor


class Resolver(ExprVisitor, StmtVisitor):
    scopes: List[Dict[str, bool]]
    locals: Dict[Expr, int]

    def __init__(self):
        self.scopes = [{}]
        self.locals = {}

    def resolve(
        self, thing: Union[Union[List[Stmt], List[Expr]], Union[Stmt, Expr]]
    ) -> Any:
        if isinstance(thing, list):
            for ting in thing:
                return self.resolve(ting)
        else:  # Else because python typing is shit
            return thing.visit(self)

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
        if not self.scopes[len(self.scopes) - 1][expr.name.lexeme]:
            raise ResolutionError("Cannot use variable in its own initializer.")

        return None

    # StmtVisitor
    def block(self, stmt: Block):
        self.open_scope()
        self.resolve(stmt.statements)
        self.close_scope()
        return None

    def let(self, stmt: Let) -> Any:
        self.declare(stmt.name.lexeme)
        if stmt.initializer:
            self.resolve(stmt.initializer)
        self.define(stmt.name.lexeme)
        return None
