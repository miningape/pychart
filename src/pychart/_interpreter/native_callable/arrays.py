from typing import Any, List, Tuple
from src.pychart._interpreter.helpers.callable import PychartCallable
from src.pychart._interpreter.visitors.interpreter import PychartArray


class ArrayMethods:
    class Push(PychartCallable):
        def __call__(self, args: List[Any]) -> Any:
            array = args[0]
            item = args[1]

            if not isinstance(array, PychartArray):
                raise RuntimeError("push's first argument must be an array")

            array.elems.append(item)
            return array

        def arity(self, args: List[Any]) -> Tuple[bool, str]:
            return (
                len(args) != 2,
                "push's first arg must be array, second must be element",
            )

    class Pop(PychartCallable):
        def __call__(self, args: List[Any]) -> Any:
            array = args[0]

            if not isinstance(array, PychartArray):
                raise RuntimeError("pop's first argument must be an array")

            if len(array.elems) == 0:
                raise RuntimeError("Cannot pop array of length 0")

            return array.elems.pop()

        def arity(self, args: List[Any]) -> Tuple[bool, str]:
            return (
                len(args) != 1,
                "push can only have one argument",
            )

    class Length(PychartCallable):
        def __call__(self, args: List[Any]) -> Any:
            array = args[0]

            if not isinstance(array, PychartArray):
                raise RuntimeError("len's first argument must be an array")

            return len(array.elems)

        def arity(self, args: List[Any]) -> Tuple[bool, str]:
            return (
                len(args) != 1,
                "push can only have one argument",
            )
