from typing import Any, Callable, Dict

from src.pychart._interpreter.token_type.token import Token
from src.pychart._interpreter.token_type.token_type_enum import TokenType


def interpret_instruction(token: Token, left: Any, right: Any) -> Any:
    instructions: Dict[TokenType, Callable[[], Any]] = {
        TokenType.STAR: lambda: left * right,
        TokenType.SLASH: lambda: left / right,
        TokenType.MINUS: lambda: left - right,
        TokenType.GREATER: lambda: left > right,
        TokenType.LESSER: lambda: left < right,
        TokenType.EQUAL_EQUAL: lambda: left == right,
        TokenType.GREATER_EQUAL: lambda: left >= right,
        TokenType.LESSER_EQUAL: lambda: left <= right,
        TokenType.BANG_EQUAL: lambda: left != right,
        TokenType.PLUS: (
            lambda: left + right
            if is_number(left) == is_number(right)
            else str(left) + str(right)
        ),
    }

    method = instructions.get(token.token_type)

    if method is not None:
        return method()

    raise RuntimeError(f"Operation {token.lexeme} is not an Arithmetic Operator")


def is_number(num: Any):
    typeof = type(num)
    return typeof == int or typeof == float


def try_cast_int(num: Any):
    if isinstance(num, (float)):
        if int(num) == num:
            return int(num)

    return num
