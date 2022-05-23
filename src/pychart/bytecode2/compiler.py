from typing import Any, Callable, Dict, List, Optional

from src.pychart._interpreter.ast_nodes.expression import (
    Assignment,
    Call,
    Expr,
    ExprVisitor,
    Binary,
    Literal,
    Variable,
)
from src.pychart._interpreter.ast_nodes.statement import (
    Block,
    Expression,
    If,
    Let,
    StmtVisitor,
    While,
)
from src.pychart._interpreter.token_type.token_type_enum import TokenType

from src.pychart.bytecode2.bytecode_interpreter import (
    Create,
    BinaryCode,
    Bytecode,
    Jump,
    JumpIf,
    JumpIfNot,
    Label,
    LiteralValue,
    Push,
    Register,
    StackValue,
    Value,
)

binary_action: Dict[TokenType, Callable[[Any, Any], Any]] = {
    TokenType.PLUS: lambda a, b: a + b,
    TokenType.MINUS: lambda a, b: a - b,
    TokenType.STAR: lambda a, b: a * b,
    TokenType.SLASH: lambda a, b: a / b,
    TokenType.GREATER: lambda a, b: a > b,
    TokenType.GREATER_EQUAL: lambda a, b: a >= b,
    TokenType.EQUAL_EQUAL: lambda a, b: a == b,
    TokenType.LESSER_EQUAL: lambda a, b: a <= b,
    TokenType.LESSER: lambda a, b: a < b,
}


class Stack:
    stack: List[Dict[str, int]] = [{}]
    name_count: List[int] = [0]

    def get(self, name: str):
        top_frame = self.stack[len(self.stack) - 1]
        if not (name in top_frame):
            self.stack[len(self.stack) - 1][name] = self.name_count[
                len(self.name_count) - 1
            ]
            self.name_count[len(self.name_count) - 1] += 1

        return self.stack[len(self.stack) - 1][name]

    def get_at(self, frame: int, name: str):
        return self.stack[frame][name]

    def push(self):
        self.stack.append({})
        self.name_count.append(0)

    def pop(self):
        self.stack.pop()
        self.name_count.pop()


class Compiler(ExprVisitor, StmtVisitor):
    resolver_bindings: Dict[Expr, int]
    uuid: int = 0
    bytecode: List[Bytecode] = []
    stack = Stack()

    def get_new_uuid(self):
        self.uuid += 1
        return str(self.uuid)

    def register(self, name: Optional[str]) -> Register:
        if name:
            return Register(f".var<{name}>")

        return Register(f".temp<{self.get_new_uuid()}>")

    def push_or_get_index(self, name: str) -> Value:
        pos = self.stack.get(name)
        self.compose(Push(None))
        return StackValue(pos)

    def compose(self, *bytecodes: Bytecode):
        for btcd in bytecodes:
            self.bytecode.append(btcd)

    def expression(self, stmt: Expression) -> Value:
        return stmt.expr(self)

    def literal(self, expr: Literal) -> Value:
        return LiteralValue(expr.value)

    def variable(self, expr: Variable) -> Value:
        return self.push_or_get_index(expr.name.lexeme)

    def assignment(self, expr: Assignment) -> Any:
        target_register = self.push_or_get_index(expr.name.lexeme)
        from_register = expr.initializer(self)

        self.compose(
            BinaryCode(
                "+",
                target_register,
                from_register,
                LiteralValue(0),
                lambda a, b: a + b,
            )
        )

        return target_register

    def let(self, stmt: Let) -> Value:
        # pos_in_stack = self.stack.get(stmt.name.lexeme)
        stack_pos = self.push_or_get_index(stmt.name.lexeme)

        if stmt.initializer:
            temp_register = stmt.initializer(self)
            self.compose(
                BinaryCode(
                    "+",
                    stack_pos,
                    temp_register,
                    LiteralValue(0),
                    lambda a, b: a + b,
                )
            )

        return stack_pos

    def binary(self, expr: Binary) -> Value:
        action = binary_action.get(expr.operator.token_type)
        assert action, f"Unsupported operator: {expr.operator.lexeme}"

        output_register = self.push_or_get_index(f".temp<{self.get_new_uuid()}>")
        left: Value = expr.left(self)
        right: Value = expr.right(self)

        self.compose(
            BinaryCode(expr.operator.lexeme, output_register, left, right, action),
        )

        return output_register

    def stitch(self, label: Label):
        self.compose(label)
        label.position = len(self.bytecode) - 1

    def block(self, stmt: Block) -> Any:
        for st in stmt.statements:
            st(self)

    def if_stmt(self, stmt: If) -> Any:
        condition_register = stmt.if_test(self)

        true_label = Label()
        exit_label = Label()

        self.compose(JumpIf(condition_register, true_label))
        if stmt.else_body:
            stmt.else_body(self)
        self.compose(Jump(exit_label))
        self.stitch(true_label)
        stmt.if_body(self)
        self.stitch(exit_label)

    def while_stmt(self, stmt: While) -> Any:
        entry_label = Label()
        exit_label = Label()

        self.stitch(entry_label)
        condition_register = stmt.while_test(self)
        self.compose(JumpIfNot(condition_register, exit_label))
        stmt.while_body(self)
        self.compose(Jump(entry_label))
        self.stitch(exit_label)

    def call(self, expr: Call) -> Any:
        return super().call(expr)
