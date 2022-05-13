from typing import Any, List, Tuple


class PychartCallable:
    @staticmethod
    def from_expr(expr: Any):
        if isinstance(expr, PychartCallable):
            return expr
        raise RuntimeError("Could not convert to callable.")

    def __call__(self, args: List[Any]) -> Any:
        raise RuntimeError("Cannot call base callable.")

    def arity(self, args: List[Any]) -> Tuple[bool, str]:
        raise RuntimeError("Cannot call base callable.")


class InputFunc(PychartCallable):
    def __call__(self, args: List[Any]) -> Any:
        return input(*args)

    def arity(self, args: List[Any]) -> Tuple[bool, str]:
        return (False, "")


class PrintFunc(PychartCallable):
    def __call__(self, args: List[Any]) -> Any:
        print(*args)
        return None

    def arity(self, args: List[Any]) -> Tuple[bool, str]:
        return (False, "")
