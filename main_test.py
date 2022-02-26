import sys
sys.path.append('src')

import pychart
import pychart.scanner
import pychart.token_type
import pychart.token_type.token_type_enum
import pychart.token_type.token

def inc(number: int) -> int:
    return number + 1


def test_answer():
    assert inc(3) == 4
