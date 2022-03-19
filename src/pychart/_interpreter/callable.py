from typing import Any, Tuple, List
from src.pychart._interpreter.environment import Environment


class PychartCallable:
    @staticmethod
    def from_expr(expr: Any):
        if isinstance(expr, PychartCallable):
            return expr
        raise RuntimeError("Could not convert to callable.")

    def __call__(self, environment: Environment, args: List[Any]) -> Any:
        raise RuntimeError("Cannot call base callable.")

    def arity(self, args: List[Any]) -> Tuple[bool, str]:
        raise RuntimeError("Cannot call base callable.")


class InputFunc(PychartCallable):
    def __call__(self, _: Environment, args: List[Any]) -> Any:
        return input(*args)

    def arity(self, args: List[Any]) -> Tuple[bool, str]:
        return (False, "")


class PrintFunc(PychartCallable):
    def __call__(self, _: Environment, args: List[Any]) -> Any:
        print(*args)
        return None

    def arity(self, args: List[Any]) -> Tuple[bool, str]:
        return (False, "")


class OrangeFunc(PychartCallable):
    def __call__(self, _: Environment, args: List[Any]) -> Any:
        return "\033[93m" + str(args[0]) + "\033[0m"

    def arity(self, args: List[Any]) -> Tuple[bool, str]:
        return (len(args) != 1, "")
