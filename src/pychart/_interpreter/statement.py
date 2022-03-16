from typing import List, Optional, Any
from src.pychart._interpreter.environment import Environment
from src.pychart._interpreter.expression import Expr, Token


class Stmt:
    def __call__(self, environment: Environment) -> Any:
        raise RuntimeError("Expected Actual Statement")

    def javascript(self) -> str:
        raise RuntimeError("JS - Expected Actual Statement")


class Expression(Stmt):
    expr: Expr

    def __init__(self, expr: Expr):
        self.expr = expr

    def __call__(self, environment: Environment):
        return self.expr(environment)

    def javascript(self) -> str:
        return self.expr.javascript() + ";"


class Print(Stmt):
    expr: Expr

    def __init__(self, expr: Expr):
        self.expr = expr

    def __call__(self, environment: Environment):
        print(self.expr(environment))
        return None

    def javascript(self) -> str:
        return f"console.log({self.expr.javascript()});"


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

    def javascript(self) -> str:
        init = ""

        if self.initializer:
            init += "=" + self.initializer.javascript()

        return f"let {self.name.lexeme}{init};"


class Block(Stmt):
    statements: List[Stmt]

    def __init__(self, statements: List[Stmt]):
        self.statements = statements

    def __call__(self, environment: Environment):
        environment = Environment(environment)

        for statement in self.statements:
            statement(environment)

    def javascript(self) -> str:
        statmentjs = "{"

        for statement in self.statements:
            statmentjs += statement.javascript()

        return statmentjs + "}"


class If(Stmt):
    test: Expr
    body: Stmt

    def __init__(self, test: Expr, body: Stmt):
        self.test = test
        self.body = body

    def __call__(self, environment: Environment):
        if self.test(environment):
            self.body(environment)

    def javascript(self) -> str:
        return f"if({self.test.javascript()}){self.body.javascript()}"
