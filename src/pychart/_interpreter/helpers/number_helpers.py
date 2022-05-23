from typing import Any


def is_number(num: Any):
    typeof = type(num)
    return typeof == int or typeof == float


def try_cast_int(num: Any):
    if isinstance(num, float):
        if int(num) == num:
            return int(num)

    return num
