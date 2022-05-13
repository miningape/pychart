from dataclasses import dataclass
from functools import wraps
from operator import truediv
from re import L
from typing import Any, Callable, Dict, List
from typing_extensions import Self


from src.pychart._interpreter.ast_nodes.expression import (
    Assignment,
    Binary,
    Expr,
    ExprVisitor,
    Grouping,
    Literal,
    Unary,
    Variable,
)
from src.pychart._interpreter.ast_nodes.statement import (
    Block,
    Expression,
    If,
    Let,
    Stmt,
    StmtVisitor,
)
from src.pychart._interpreter.helpers.environment import Environment
from src.pychart._interpreter.helpers.number_helpers import interpret_instruction
from src.pychart._interpreter.token_type.token import Token
from src.pychart._interpreter.token_type.token_type_enum import TokenType

commandQueue: List["Command"] = []


class VMState:
    stack: List[Any]
    instructions: List["Command"]
    instruction_pointer: int
    environment: Environment

    is_done: bool

    def __init__(self, instructions: List["Command"]):
        self.stack = []
        self.instructions = instructions
        self.instruction_pointer = 0
        self.environment = Environment()

        self.is_done = False


def run_virtual_machine(vm_state: VMState):
    while vm_state.instruction_pointer < len(vm_state.instructions):
        vm_state = vm_state.instructions[vm_state.instruction_pointer].execute(vm_state)
        # print(vm_state.instruction_pointer, vm_state.stack)


def run_jit_machine(vm_state: VMState):
    iterations = 0
    while len(commandQueue) > 0 and iterations < 3:
        command = commandQueue.pop()
        vm_state.instructions.append(command)
        iterations += 1

    for _ in range(2):
        vm_state = vm_state.instructions[vm_state.instruction_pointer].execute(vm_state)

    run_jit_machine(vm_state)


def move_instruction_pointer(steps: int = 1):
    def decorator(func: Callable[[Any, VMState], VMState]):
        @wraps(func)
        def wrapper(self: Any, vm_state: VMState):
            # print(self)
            vm_state = func(self, vm_state)
            vm_state.instruction_pointer += steps
            return vm_state

        return wrapper

    return decorator


class Command:
    def execute(self, vm_state: VMState) -> VMState:
        raise Exception()


class JumpBase(Command):
    jump_to: int


@dataclass
class JumpIfFalse(JumpBase):
    jump_to: int

    @move_instruction_pointer(0)
    def execute(self, vm_state: VMState) -> VMState:
        test = vm_state.stack.pop()

        state = test is False

        vm_state.instruction_pointer = (self.jump_to * state) + (
            vm_state.instruction_pointer + 1
        ) * (1 - state)

        return vm_state


@dataclass
class Jump(JumpBase):
    jump_to: int

    @move_instruction_pointer(0)
    def execute(self, vm_state: VMState) -> VMState:
        vm_state.instruction_pointer = self.jump_to
        return vm_state


class CommandStack:
    @dataclass(frozen=True)
    class Push(Command):
        value: Any

        @move_instruction_pointer()
        def execute(self, vm_state: VMState):
            vm_state.stack.append(self.value)
            return vm_state

    @dataclass(frozen=True)
    class Pop(Command):
        @move_instruction_pointer()
        def execute(self, vm_state: VMState):
            vm_state.stack.pop()
            return vm_state


class CommandEnv:
    @dataclass(frozen=True)
    class Push(Command):
        @move_instruction_pointer()
        def execute(self, vm_state: VMState):
            vm_state.environment = Environment(vm_state.environment)
            return vm_state

    @dataclass(frozen=True)
    class Pop(Command):
        @move_instruction_pointer()
        def execute(self, vm_state: VMState):
            if not vm_state.environment.enclosing:
                raise Exception("Attempting to pop global env")

            vm_state.environment = vm_state.environment.enclosing
            return vm_state

    @dataclass(frozen=True)
    class Set(Command):
        variable: Assignment
        depth: int

        @move_instruction_pointer()
        def execute(self, vm_state: VMState) -> VMState:
            value = vm_state.stack[len(vm_state.stack) - 1]
            vm_state.environment.set_at(self.depth, self.variable.name.lexeme, value)
            return vm_state

    @dataclass(frozen=True)
    class Get(Command):
        variable: Variable
        depth: int

        @move_instruction_pointer()
        def execute(self, vm_state: VMState) -> VMState:
            value = vm_state.environment.get_at(self.depth, self.variable.name.lexeme)
            vm_state.stack.append(value)
            return vm_state

    @dataclass(frozen=True)
    class Create(Command):
        variable: Let
        initialiser: bool

        @move_instruction_pointer()
        def execute(self, vm_state: VMState) -> VMState:
            value = None
            if self.initialiser:
                value = vm_state.stack.pop()
            vm_state.environment.reverve(self.variable.name.lexeme, value)
            return vm_state


@dataclass(frozen=True)
class NegateCommand(Command):
    @move_instruction_pointer()
    def execute(self, vm_state: VMState) -> VMState:
        top = vm_state.stack.pop()
        vm_state.stack.append(not top)
        return vm_state


@dataclass(frozen=True)
class ArithmaticCommand(Command):
    operator: Token

    @move_instruction_pointer()
    def execute(self, vm_state: VMState) -> VMState:

        right = vm_state.stack.pop()
        left = vm_state.stack.pop()

        value = interpret_instruction(self.operator, left, right)
        vm_state.stack.append(value)

        return vm_state


class Compiler(ExprVisitor, StmtVisitor):
    resolver_bindings: Dict[Expr, int]
    commandQueue: List["Command"] = []
    num_labels = 0

    def __init__(self, resolver_bindings: Dict[Expr, int]):
        self.resolver_bindings = resolver_bindings

    def emit(self, command: Command):
        self.commandQueue.append(command)

    def command_num(self):
        return len(self.commandQueue)

    def patch_jump(self, pos: int, jump_to: int):
        cmd = self.commandQueue[pos]

        if not isinstance(cmd, JumpBase):
            raise Exception("Cmd target is not a jump")

        cmd.jump_to = jump_to

    def binary(self, expr: Binary) -> Any:
        expr.left(self)
        expr.right(self)

        self.emit(ArithmaticCommand(expr.operator))

    def literal(self, expr: Literal) -> Any:
        self.emit(CommandStack.Push(expr.value))

    def grouping(self, expr: Grouping) -> Any:
        expr.expr(self)

    def unary(self, expr: Unary) -> Any:
        if expr.operator.token_type is TokenType.BANG:
            return self.emit(NegateCommand())

        if expr.operator.token_type is TokenType.MINUS:
            self.emit(CommandStack.Push(0))
            expr.right(self)
            self.emit(ArithmaticCommand(expr.operator))

        raise Exception()

    def variable(self, expr: Variable) -> Any:
        depth = self.resolver_bindings.get(expr)

        if depth is None:
            raise RuntimeError(f"GET: Could not resolve variable: '{expr.name.lexeme}'")

        self.emit(CommandEnv.Get(expr, depth))

    def assignment(self, expr: Assignment) -> Any:
        expr.initializer(self)

        depth = self.resolver_bindings.get(expr)

        if depth is None:
            raise RuntimeError(f"GET: Could not resolve variable: '{expr.name.lexeme}'")

        self.emit(CommandEnv.Set(expr, depth))

    def let(self, stmt: Let) -> Any:
        if stmt.initializer is not None:
            stmt.initializer(self)

        self.emit(CommandEnv.Create(stmt, stmt.initializer is not None))

    def block(self, stmt: Block) -> Any:
        self.emit(CommandEnv.Push())

        for statement in stmt.statements:
            statement(self)

        self.emit(CommandEnv.Pop())

    def emit_jump_if_false(self):
        self.emit(JumpIfFalse(-1))
        return self.command_num() - 1

    def emit_jump(self):
        self.emit(Jump(-1))
        return self.command_num() - 1

    def if_stmt(self, stmt: If) -> Any:
        stmt.if_test(self)  # Add test conditions to program
        jump_to_end = self.emit_jump_if_false()  # Jump if false to else block
        stmt.if_body(self)  # Add body
        if stmt.else_body:
            jump_to_else_end = self.emit_jump()  # Jump to end (skip else block)
            self.patch_jump(jump_to_end, self.command_num())  # Mark else block
            stmt.else_body(self)  # Add else block
            self.patch_jump(jump_to_else_end, self.command_num())  # mark end of `if`
        else:
            self.patch_jump(jump_to_end, self.command_num())  # Mark else block

    def expression(self, stmt: Expression) -> Any:
        stmt.expr(self)

        self.emit(CommandStack.Pop())


if __name__ == "__main__":
    PLUS = Token(TokenType.PLUS, "+", None, 0)
    TIMES = Token(TokenType.STAR, "*", None, 0)

    # expr = Binary(Literal(1), PLUS, Binary(Literal(2), TIMES, Literal(3)))
    compiler = Compiler({})

    # expr(compiler)
