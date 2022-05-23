from copy import deepcopy
from dataclasses import dataclass
from distutils.errors import CompileError
from typing import Any, List, Tuple

from src.pychart._interpreter.ast_nodes.expression import (
    Assignment,
    Call,
    ExprVisitor,
    Binary,
    Grouping,
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
from src.pychart._interpreter.token_type.token_type_enum import TokenType


class StackVM:
    # Data structures
    stack: List[Any] = []
    frames: List[int] = [0]
    instruction_pointer: int = 0
    done: bool = False

    # Stack manipulation
    def push(self, value: Any):
        self.stack.append(value)

    def pop(self) -> Any:
        return self.stack.pop()

    def top(self) -> Any:
        return self.stack[len(self.stack) - 1]

    def get(self, index: int) -> Any:
        return self.stack[index]


class Bytecode:
    def execute(self, vm: StackVM) -> Any:
        pass


def interpret_stack_code(bytecodes: List[Bytecode]):
    bytecodes.append(EOF())
    vm = StackVM()

    while not vm.done:
        bytecodes[vm.instruction_pointer].execute(vm)
        print(
            f"{vm.instruction_pointer} : {bytecodes[vm.instruction_pointer]} -> stack={vm.stack} frames={vm.frames}"
        )
        vm.instruction_pointer += 1


@dataclass
class Push(Bytecode):
    value: Any

    def execute(self, vm: StackVM):
        vm.push(self.value)


@dataclass
class Get(Bytecode):
    index: int

    def execute(self, vm: StackVM) -> Any:
        vm.push(vm.stack[self.index])


@dataclass
class Set(Bytecode):
    index: int

    def execute(self, vm: StackVM) -> Any:
        vm.stack[self.index] = vm.top()


@dataclass
class Label(Bytecode):
    location: int = -10

    def execute(self, vm: StackVM) -> Any:
        pass  # Do nothing go to next instruction


@dataclass
class Jump(Bytecode):
    label: Label

    def execute(self, vm: StackVM) -> Any:
        vm.instruction_pointer = self.label.location


@dataclass
class JumpIfNot(Bytecode):
    label: Label

    def execute(self, vm: StackVM):
        should_jump = not vm.pop()
        if should_jump:
            vm.instruction_pointer = self.label.location


@dataclass
class Add(Bytecode):
    def execute(self, vm: StackVM) -> Any:
        right = vm.pop()

        vm.stack[len(vm.stack) - 1] += right


@dataclass
class EOF(Bytecode):
    def execute(self, vm: StackVM) -> Any:
        vm.done = True


@dataclass
class Sub(Bytecode):
    def execute(self, vm: StackVM) -> Any:
        right = vm.pop()

        vm.stack[len(vm.stack) - 1] -= right


@dataclass
class Mul(Bytecode):
    def execute(self, vm: StackVM) -> Any:
        right = vm.pop()

        vm.stack[len(vm.stack) - 1] *= right


@dataclass
class Div(Bytecode):
    def execute(self, vm: StackVM) -> Any:
        right = vm.pop()

        vm.stack[len(vm.stack) - 1] /= right


@dataclass
class GTE(Bytecode):
    def execute(self, vm: StackVM) -> Any:
        right = vm.pop()

        vm.stack[len(vm.stack) - 1] = vm.stack[len(vm.stack) - 1] >= right


@dataclass
class LTE(Bytecode):
    def execute(self, vm: StackVM) -> Any:
        right = vm.pop()

        vm.stack[len(vm.stack) - 1] = vm.stack[len(vm.stack) - 1] <= right


@dataclass
class LT(Bytecode):
    def execute(self, vm: StackVM) -> Any:
        right = vm.pop()

        vm.stack[len(vm.stack) - 1] = vm.stack[len(vm.stack) - 1] < right


@dataclass
class EE(Bytecode):
    def execute(self, vm: StackVM) -> Any:
        right = vm.pop()

        vm.stack[len(vm.stack) - 1] = vm.stack[len(vm.stack) - 1] == right


@dataclass
class GT(Bytecode):
    def execute(self, vm: StackVM) -> Any:
        right = vm.pop()

        vm.stack[len(vm.stack) - 1] = vm.stack[len(vm.stack) - 1] > right


@dataclass
class Not(Bytecode):
    def execute(self, vm: StackVM) -> Any:
        vm.stack[len(vm.stack) - 1] = not vm.stack[len(vm.stack) - 1]


SYMBOL_TO_BYTECODE = {
    "+": Add(),
    "-": Sub(),
    "*": Mul(),
    "/": Div(),
    ">=": GTE(),
    ">": GT(),
    "==": EE(),
    "<": LT(),
    "<=": LTE(),
}


@dataclass
class Pop(Bytecode):
    def execute(self, vm: StackVM) -> Any:
        return vm.pop()


@dataclass
class SnapShot:
    frames: List[int]
    location: int


@dataclass
class StackFn:
    location: int
    stack: List[Any]
    frames: List[int]


@dataclass
class GetAt(Bytecode):
    frame: int
    offset: int

    def execute(self, vm: StackVM) -> Any:
        index = vm.frames[len(vm.frames) - 1 - self.frame]
        vm.push(vm.stack[index + self.offset])


@dataclass
class SetAt(Bytecode):
    frame: int
    offset: int

    def execute(self, vm: StackVM) -> Any:
        index = vm.frames[len(vm.frames) - 1 - self.frame]
        vm.stack[index + self.offset] = vm.top()


@dataclass
class CALL(Bytecode):
    args: int

    def execute(self, vm: StackVM) -> Any:
        func = vm.top()
        assert isinstance(func, StackFn)

        snapshot = SnapShot([], vm.instruction_pointer)
        vm.push(snapshot)

        # Save the frame before the args, self, return
        vm.frames.append(len(vm.stack) - self.args - 2)

        # Save the frames currently being executed
        snapshot.frames = vm.frames.copy()

        # vm.frames = func.frames.copy()  # merge frames
        # 0 -> Before args = current frame
        # args from current frame
        # rest from func definition

        # for i in vm.frames:
        #     func.frames = i

        vm.instruction_pointer = func.location


@dataclass
class Routine(Bytecode):
    end: Label

    def execute(self, vm: StackVM) -> Any:
        location = vm.instruction_pointer

        # stack =

        stackfn = StackFn(location, [], [])

        vm.push(stackfn)

        stackfn.stack = vm.stack.copy()
        stackfn.frames = vm.frames.copy() + [len(vm.stack)]

        vm.instruction_pointer = self.end.location


@dataclass
class RET(Bytecode):
    def execute(self, vm: StackVM) -> Any:
        value = vm.pop()
        snapshot = vm.pop()
        assert isinstance(snapshot, SnapShot)

        # Clear stack frames
        # vm.frames = snapshot.frames.copy()
        old_stack_size = vm.frames.pop()
        while len(vm.stack) > old_stack_size:
            vm.pop()

        vm.push(value)
        vm.instruction_pointer = snapshot.location


class Compiler(ExprVisitor, StmtVisitor):
    instructions: List[Bytecode] = []

    stack: List[str] = []
    stack_frames: List[int] = [0]
    break_stack: List[Tuple[Label, int]] = []

    def index_of(self, var_name: str):
        prev = len(self.stack)
        for frame, index in reversed(list(enumerate(self.stack_frames))):
            for i in range(index, prev):
                offset = i - index
                name = self.stack[i]
                if var_name == name:
                    return (len(self.stack_frames) - (frame + 1), offset)

        raise RuntimeError(f"Unbound variable {var_name}")

    def push(self, *ins: Bytecode):
        for instruction in ins:
            self.instructions.append(instruction)

    def stitch(self, label: Label):
        label.location = len(self.instructions)
        self.push(label)

    def variable(self, expr: Variable) -> Any:
        index, off = self.index_of(expr.name.lexeme)
        self.push(GetAt(index, off))

    def literal(self, expr: Literal) -> Any:
        self.push(Push(expr.value))

    def assignment(self, expr: Assignment) -> Any:
        index, off = self.index_of(expr.name.lexeme)
        expr.initializer(self)
        self.push(SetAt(index, off))

    def binary(self, expr: Binary) -> Any:
        expr.left(self)
        expr.right(self)

        bytecode = SYMBOL_TO_BYTECODE.get(expr.operator.lexeme)

        if not bytecode:
            raise Exception("Unimplemented symbol")

        self.push(bytecode)

    def unary(self, expr: Unary) -> Any:
        if expr.operator.token_type is TokenType.BANG:
            expr.right(self)
            self.push(Not())

        elif expr.operator.token_type is TokenType.MINUS:
            self.push(Push(0))
            expr.right(self)
            self.push(Sub())

        else:
            raise CompileError(f"Unknown operator: {expr.operator.lexeme}")

    def call(self, expr: Call) -> Any:
        for arg in expr.arguments:
            arg(self)

        expr.callee(self)
        self.push(CALL(len(expr.arguments)))

    def return_stmt(self, stmt: Return) -> Any:
        print("return")
        index, off = self.index_of("return_pointer")
        self.push(GetAt(index, off))
        stmt.expr(self)
        self.push(RET())

    def function(self, stmt: Function) -> Any:
        print(stmt.name.lexeme, self.stack, self.stack_frames)
        end = Label()

        self.stack.append(stmt.name.lexeme)

        self.stack_frames.append(len(self.stack))

        for name in stmt.params:
            self.stack.append(name.lexeme)
        self.stack.append(stmt.name.lexeme)
        self.stack.append("return_pointer")
        index, off = self.index_of("return_pointer")

        self.push(Routine(end))
        for statement in stmt.body:
            print(stmt.name.lexeme, self.stack, self.stack_frames)
            statement(self)

        self.push(GetAt(index, off), Push(None), RET())
        self.stitch(end)

        size = self.stack_frames.pop()
        while len(self.stack) > size:
            self.stack.pop()

    def block(self, stmt: Block) -> Any:
        self.stack_frames.append(len(self.stack))

        for statement in stmt.statements:
            statement(self)

        stack_size = self.stack_frames.pop()
        while len(self.stack) > stack_size:
            self.stack.pop()
            self.push(Pop())

    def expression(self, stmt: Expression) -> Any:
        stmt.expr(self)
        self.push(Pop())

    def let(self, stmt: Let) -> Any:
        if stmt.initializer:
            stmt.initializer(self)
        else:
            self.push(Push(None))

        name = stmt.name.lexeme
        self.stack.append(name)

    def if_stmt(self, stmt: If) -> Any:
        ext = Label()

        stmt.if_test(self)
        self.push(JumpIfNot(ext))
        stmt.if_body(self)

        if not stmt.else_body:
            self.stitch(ext)
            return

        skip = Label()

        self.push(Jump(skip))
        self.stitch(ext)
        stmt.else_body(self)
        self.stitch(skip)

    def break_stmt(self, stmt: Break) -> Any:
        top = len(self.break_stack) - 1
        if top < 0:
            raise CompileError("Cannot `Break` outside of a while loop")

        exit_label, stack_size = self.break_stack[top]

        diff = len(self.stack) - stack_size

        for _ in range(diff):
            self.push(Pop())

        self.push(Jump(exit_label))

    def grouping(self, expr: Grouping) -> Any:
        expr.expr(self)

    def while_stmt(self, stmt: While) -> Any:
        top = Label()
        ext = Label()

        self.break_stack.append((ext, len(self.stack)))

        self.stitch(top)
        stmt.while_test(self)
        self.push(JumpIfNot(ext))
        stmt.while_body(self)
        self.push(Jump(top))
        self.stitch(ext)

        self.break_stack.pop()


# pylint:disable=pointless-string-statement
"""
func jeff(n) {
    print(n);
}

jeff("Hello World");

---------------------

ROUTINE (label=end)
ASSERT
GET 2
PRINT
POPPOPPOP
RET
LABEL end

FRAME
PUSH 393
PUSH 1
PUSH "Hello World"
CALL 0

---------------------
ROUTINE stack=[heap(1)] heap=[fn<[heap(0)],[0, 1],381>] stackframes=[0]
LABEL end

FRAME stackframes=[0, 1]
PUSH return<389> stack=[heap(1), "Hello World", return<389, 1>] heap=[fn<[heap(1)],[1],381>]
PUSH "Hello, World" stack=[heap(1), "Hello World"] heap=[fn<[],[], 381>]
CALL 0 ; Gets heap entry, merges stacks 
ASSERT ; checks if (GET 1) + 2 + frame top = stack size


assert


stack pointer + offset

----------------------
ROUTINE end ; stack = [self, <loc, frames> a, b] frames=[0, 1]
GET 1
GET 2
ADD
RET
end

PUSH 20

; stack = [fn<top>]
PUSH 1
PUSH 2
GET 0
CALL
ret

stack=[fn]
stack=[fn, 20]
stack=[fn, 20, 1]
stack=[fn, 20, 1, 2]
stack=[fn, 20, 1, 2, fn]
stack=[fn, 20, 1, 2, activation]
stack=[fn, 20, 1, 2]


"""
