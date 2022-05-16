from copy import deepcopy
from typing import Any, Dict, List, Tuple
from src.pychart._interpreter.ast_nodes.expression import (
    Array,
    Assignment,
    Binary,
    Call,
    Expr,
    ExprVisitor,
    Grouping,
    Index,
    IndexSet,
    Literal,
    Unary,
    Variable,
)
from src.pychart._interpreter.ast_nodes.statement import (
    Block,
    Break,
    Expression,
    Function,
    If,
    Let,
    Return,
    StmtVisitor,
    While,
)
from src.pychart._interpreter.helpers.callable import PychartCallable
from src.pychart._interpreter.helpers.environment import Environment
from src.pychart._interpreter.helpers.number_helpers import (
    interpret_instruction,
    try_cast_int,
)
from src.pychart._interpreter.helpers.indexable import PychartIndexable
from src.pychart._interpreter.helpers.number_helpers import is_number, try_cast_int
from src.pychart._interpreter.token_type.token import Token
from src.pychart._interpreter.token_type.token_type_enum import TokenType


class BreakStatementException(Exception):
    pass


class ReturnValue(Exception):
    value: Any

    def __init__(self, value: Any) -> None:
        super().__init__("Cannot `return` outside of a function")
        self.value = value


class Interpreter(ExprVisitor, StmtVisitor):
    environment: Environment
    resolver_bindings: Dict[Expr, int]

    def __init__(self, resolver_bindings: Dict[Expr, int]):
        self.environment = Environment()
        self.resolver_bindings = resolver_bindings

    def get(self, name: Token, expr: Expr):
        depth = self.resolver_bindings.get(expr)

        if depth is None:
            raise RuntimeError(f"GET: Could not resolve variable: '{name.lexeme}'")

        return self.environment.get_at(depth, name.lexeme)

    def set(self, name: Token, expr: Expr, value: Any):
        depth = self.resolver_bindings.get(expr)

        if depth is None:
            raise RuntimeError(f"SET: Could not resolve variable: '{name.lexeme}'")

        return self.environment.set_at(depth, name.lexeme, value)

    # Expression Visitor
    def binary(self, expr: Binary) -> Any:
        left = expr.left(self)
        right = expr.right(self)

        return interpret_instruction(expr.operator, left, right)

    def unary(self, expr: Unary) -> Any:
        right = expr.right(self)

        if expr.operator.token_type == TokenType.MINUS:
            return 0 - right
        elif expr.operator.token_type == TokenType.BANG:
            return not right

        raise RuntimeError("Call Unary Undefined")

    def literal(self, expr: Literal) -> Any:
        return try_cast_int(expr.value)

    def grouping(self, expr: Grouping) -> Any:
        return expr.expr(self)

    def variable(self, expr: Variable) -> Any:
        return self.get(expr.name, expr)

    def assignment(self, expr: Assignment) -> Any:
        value = expr.initializer(self)

        self.set(expr.name, expr, value)

        return value

    def call(self, expr: Call) -> Any:
        callee_eval: Any = expr.callee(self)

        args: List[Any] = []
        for arg in expr.arguments:
            # Evaluate arg then append
            args.append(arg(self))

        # Coercing type
        callable_fn = PychartCallable.from_expr(callee_eval)

        error, message = callable_fn.arity(args)
        if error:
            raise RuntimeError(
                message
                # f"Too many arguments for function expected {callable_fn.arity()} but got {len(args)}"
            )

        return callable_fn(args)

    def array(self, expr: Array) -> Any:
        elems: List[Any] = []

        for item in expr.elems:
            elems.append(item(self))

        return PychartArray(elems)

    def index(self, expr: Index) -> Any:
        indexable = PychartIndexable.from_expr(expr.indexee(self))
        return indexable.get(expr.index(self))

    def indexset(self, expr: IndexSet) -> Any:
        indexable = PychartIndexable.from_expr(expr.index.indexee(self))

        index = expr.index.index(self)
        value = expr.value(self)

        return indexable.set(index, value)

    # Statement Visitor
    def expression(self, stmt: Expression) -> Any:
        return stmt.expr(self)

    def return_stmt(self, stmt: Return) -> Any:
        value = stmt.expr(self)
        raise ReturnValue(value)

    def let(self, stmt: Let) -> Any:
        value = None
        if stmt.initializer is not None:
            value = stmt.initializer(self)

        self.environment.reverve(stmt.name.lexeme, value)

        return value

    def block(self, stmt: Block) -> Any:
        previous = self.environment
        self.environment = Environment(self.environment)

        for statement in stmt.statements:
            statement(self)

        self.environment = previous

    def function(self, stmt: Function) -> Any:
        # print(self.environment.values)
        fncallable = PychartFunction(stmt, self)

        self.environment.reverve(stmt.name.lexeme, fncallable)
        return fncallable

    def if_stmt(self, stmt: If) -> Any:
        test_result = stmt.if_test(self)
        if test_result:
            stmt.if_body(self)
        elif stmt.else_body:
            stmt.else_body(self)

    def while_stmt(self, stmt: While) -> Any:
        while stmt.while_test(self):
            try:
                stmt.while_body(self)
            except BreakStatementException:
                break
        return None

    def break_stmt(self, stmt: Break) -> Any:
        raise BreakStatementException("Cannot invoke 'break;' outside of a while loop")


class PychartArray(PychartIndexable):
    elems: List[Any]

    def __init__(self, elems: List[Any]) -> None:
        self.elems = elems

    def set(self, index: Any, value: Any) -> Any:
        if not isinstance(index, int):
            raise RuntimeError(f'Array index "{index}" is not an integer')

        if index >= len(self.elems) or index < 0:
            raise RuntimeError(f'Array index "{index}" is out of bounds')

        self.elems[index] = value

        return value

    def get(self, index: Any):
        if not isinstance(index, int):
            raise RuntimeError(f'Array index "{index}" is not an integer')

        if index >= len(self.elems) or index < 0:
            raise RuntimeError(f'Array index "{index}" is out of bounds')

        return self.elems[index]

    def __str__(self) -> str:
        string = "["

        for elem in self.elems:
            string += str(elem) + ", "

        return string + "]"


class PychartFunction(PychartCallable):
    definition: Function
    interpreter: Interpreter
    closure: Environment

    def __init__(
        self,
        definition: Function,
        interpreter: Interpreter,
    ) -> None:
        self.definition = definition
        self.interpreter = interpreter
        self.closure = interpreter.environment

    def __str__(self) -> str:
        return f'<Function "{self.definition.name.lexeme}">'

    def __call__(self, args: List[Any]) -> Any:
        previous = self.interpreter.environment
        self.interpreter.environment = Environment(self.closure)

        # pylint: disable=consider-using-enumerate
        for i in range(len(args)):
            self.interpreter.environment.reverve(
                self.definition.params[i].lexeme, deepcopy(args[i])
            )
        # pylint: enable=consider-using-enumerate

        value = None
        try:
            for statement in self.definition.body:
                statement(self.interpreter)
        except ReturnValue as ret:
            value = ret.value

        self.interpreter.environment = previous

        return value

    def arity(self, args: List[Any]) -> Tuple[bool, str]:
        return (
            len(self.definition.params) != len(args),
            f"Wrong amount of args used to call {self.definition.name.lexeme}, expected {len(self.definition.params)} got {len(args)}",
        )
