import sys
sys.path.append('src')

import pychart

def inc(number: int) -> int:
    return number + 1


def test_answer():
    assert inc(3) == 4
