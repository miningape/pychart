import sys

sys.path.append("src")


# Are these supposed to be tests? tf
import pychart
import pychart.runner


def inc(number: int) -> int:
    return number + 1


def test_answer():
    assert inc(3) == 4
