from typing import Any, List, Tuple
from src.pychart._interpreter.helpers.callable import PychartCallable


class StoN(PychartCallable):
    def __call__(self, args: List[Any]) -> Any:
        return int(args[0])

    def arity(self, args: List[Any]) -> Tuple[bool, str]:
        return (
            len(args) != 1,
            "ntos can only have one argument",
        )
