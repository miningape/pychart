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
    
    def bytecode_execute(self, interpreter: Any, params: List[Any]):
        result = []
        for param in params:
            val = interpreter.get(param)
            if isinstance(val, dict):
                val = list(val)
            result.append(val)
        return self(result)


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
