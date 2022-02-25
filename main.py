from shutil import ExecError
import sys
from typing import List

from src.pychart.runner import run_file, run_prompt


def main(argc: int, argv: List[str]):
    if argc > 2:
        raise ExecError("Too many arguments")
    elif argc == 2:
        run_file(argv[1])
    else:
        run_prompt()


if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
