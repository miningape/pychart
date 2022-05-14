from typing import Any


class PychartIndexable:
    @staticmethod
    def from_expr(expr: Any):
        if isinstance(expr, PychartIndexable):
            return expr
        raise RuntimeError("Not indexable")

    def get(self, index: Any) -> Any:
        raise RuntimeError("Cannot index base indexable")

    def set(self, index: Any, value: Any) -> Any:
        raise RuntimeError("Cannot index base indexable")
