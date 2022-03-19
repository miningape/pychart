from typing import List, Optional, Any, Tuple
from src.pychart._interpreter.callable import PychartCallable
from src.pychart._interpreter.environment import Environment
from src.pychart._interpreter.expression import Expr, Token
from src.pychart._interpreter.token_type.token_type_enum import TokenType


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
        block_environment = Environment(environment)

        for statement in self.statements:
            statement(block_environment)


class LambdaFunction(Expr):
    params: List[Token]
    body: List[Stmt]

    def __init__(self, params: List[Token], body: List[Stmt]):
        self.params = params
        self.body = body

    def __call__(self, environment: Environment) -> Any:
        return self.PychartAnonFunction(self)

    class PychartAnonFunction(PychartCallable):
        definition: "LambdaFunction"

        def __init__(self, definition: "LambdaFunction") -> None:
            self.definition = definition

        def __str__(self):
            return "<Anonymous Function>"

        def arity(self, args: List[Any]) -> Tuple[bool, str]:
            return (
                len(self.definition.params) != len(args),
                "Wrong amount of args used to call anonymous function",
            )

        def __call__(self, environment: Environment, args: List[Any]) -> None:
            function_environment = Environment(environment)

            # pylint: disable=consider-using-enumerate
            for i in range(len(args)):
                function_environment.reverve(self.definition.params[i].lexeme, args[i])
            # pylint: enable=consider-using-enumerate

            for statement in self.definition.body:
                statement(function_environment)


class Function(Stmt):
    name: Token
    params: List[Token]
    body: List[Stmt]

    def __init__(self, name: Token, params: List[Token], body: List[Stmt]):
        self.name = name
        self.params = params
        self.body = body

    def __call__(self, environment: Environment) -> Any:
        environment.reverve(self.name.lexeme, Function.PychartFunction(self))
        return None

    class PychartFunction(PychartCallable):
        definition: "Function"

        def __init__(self, definition: "Function") -> None:
            self.definition = definition

        def __str__(self) -> str:
            return f'<Function "{self.definition.name.lexeme}">'

        def __call__(self, environment: Environment, args: List[Any]) -> Any:
            function_environment = Environment(environment)

            # pylint: disable=consider-using-enumerate
            for i in range(len(args)):
                function_environment.reverve(self.definition.params[i].lexeme, args[i])
            # pylint: enable=consider-using-enumerate

            for statement in self.definition.body:
                statement(function_environment)

        def arity(self, args: List[Any]) -> Tuple[bool, str]:
            return (
                len(self.definition.params) != len(args),
                f"Wrong amount of args used to call {self.definition.name.lexeme}, expected {len(self.definition.params)} got {len(args)}",
            )


class AnonFunction(Function, Expr):
    def __init__(self, params: List[Token], body: List[Stmt]):
        name = Token(TokenType.IDENTIFIER, "Anonymous function", None, 0)
        super().__init__(name, params, body)

    def __call__(self, environment: Environment):
        return Function.PychartFunction(self)
