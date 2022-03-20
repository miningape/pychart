from typing import Any, List, Tuple
from src.pychart._interpreter.callable import PychartCallable
from src.pychart._interpreter.environment import Environment


class PychartFileIO(PychartCallable):
    def __call__(self, _: Environment, args: List[Any]) -> Any:
        try:
            operation = str(args[0])
        except:
            raise RuntimeError(f"Cannot convert '{args[0]}' to string")

        def get_callable():
            if operation == "read":
                return PychartFileIO.Read()

            if operation == "write":
                return PychartFileIO.Write()

            raise RuntimeError(f"Cannot match '{operation}' to read/write")

        callablefn = get_callable()

        if len(args) == 1:
            return callablefn

        try:
            filename = str(args[1])
        except:
            raise RuntimeError(f"Cannot convert '{args[1]}' to string")

        return callablefn(_, [filename])

    def arity(self, args: List[Any]) -> Tuple[bool, str]:
        return (not (len(args) == 2 or len(args) == 1), "Takes 2 args")

    class Write(PychartCallable):
        def __call__(self, environment: Environment, args: List[Any]) -> Any:
            try:
                filename = str(args[0])
                contents = str(args[1])
            except:
                raise RuntimeError(f"Cannot convert '{args[0]}' to string")

            with open(filename, "w") as file:
                file.write(contents)

        def arity(self, args: List[Any]) -> Tuple[bool, str]:
            return (len(args) != 2, "Write takes 2 arguments")

    class Read(PychartCallable):
        def __call__(self, _: Environment, args: List[Any]) -> str:
            try:
                filename = str(args[0])
            except:
                raise RuntimeError(f"Cannot convert '{args[0]}' to string")

            try:
                with open(filename, "r", encoding="utf8") as file:
                    contents = "".join(file.readlines())

                return contents
            except:
                raise RuntimeError(f"Couldnt open file '{args[0]}'")

        def arity(self, args: List[Any]) -> Tuple[bool, str]:
            return (len(args) != 1, "Read File can only has one arg")
