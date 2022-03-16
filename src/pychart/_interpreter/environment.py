from typing import Any, Dict, Optional


class Environment:
    values: Dict[str, Any]
    enclosing: Optional["Environment"]

    def __init__(self, enclosing: Optional["Environment"] = None):
        self.values = {}
        self.enclosing = enclosing

    def retrieve(self, key: str) -> Any:
        if key in self.values:
            return self.values.get(key)

        if self.enclosing is not None:
            return self.enclosing.retrieve(key)

        raise RuntimeError(f"Variable {key} is not defined")

    def mutate(self, key: str, value: Any) -> Any:
        if key in self.values:
            self.values[key] = value
            return value

        if self.enclosing is not None:
            return self.enclosing.mutate(key, value)

        raise RuntimeError(f"Variable {key} not initialized")

    def reverve(self, key: str, value: Any):
        if key in self.values:
            raise RuntimeError(f"Variable {key} is already defined")

        self.values[key] = value
