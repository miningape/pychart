from typing import Any, List
from src.pychart._interpreter.environment import Environment


class PychartCallable:
    @staticmethod
    def from_expr(expr: Any):
        if isinstance(expr, PychartCallable):
            return expr
        raise RuntimeError("Could not convert to callable.")

    def __call__(self, environment: Environment, args: List[Any]) -> Any:
        raise RuntimeError("Cannot call base callable.")

    def arity(self) -> int:
        raise RuntimeError("Cannot call base callable.")


class InputFunc(PychartCallable):
    def __call__(self, environment: Environment, args: List[Any]) -> Any:
        return input(args[0])

    def arity(self) -> int:
        return 1
