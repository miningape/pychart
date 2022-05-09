from typing import Any, Dict, Optional


class Environment:
    values: Dict[str, Any]
    enclosing: Optional["Environment"]

    def __init__(self, enclosing: Optional["Environment"] = None):
        self.values = {}
        self.enclosing = enclosing

    # Probably should merge this into earlier definitions mutate and reserve
    def ancestor(self, depth: int):
        environment = self
        for _ in range(depth):
            if not environment.enclosing:
                raise RuntimeError("Resolver resolved deeper than currently exists")
            environment = environment.enclosing

        return environment

    def get_at(self, depth: int, key: str) -> Any:
        return self.ancestor(depth).get(key)

    def set_at(self, depth: int, key: str, value: Any):
        self.ancestor(depth).set(key, value)

    def get(self, key: str) -> Any:
        if key in self.values:
            return self.values[key]

        if self.enclosing is not None:
            return self.enclosing.get(key)

        raise RuntimeError(f"Variable {key} is not defined")

    def set(self, key: str, value: Any) -> Any:
        if key in self.values:
            self.values[key] = value
            return value

        if self.enclosing is not None:
            return self.enclosing.set(key, value)

        raise RuntimeError(f"Variable {key} not initialized")

    def reverve(self, key: str, value: Any):
        if key in self.values:
            raise RuntimeError(f"Variable {key} is already defined")

        self.values[key] = value

    @staticmethod
    def print(env: "Environment", layer: int = 0):
        print(layer, env.values)
        if env.enclosing:
            Environment.print(env.enclosing, layer + 1)
