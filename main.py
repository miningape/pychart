from shutil import ExecError
import sys
from typing import List


def run(source: str):
    print(source)


def run_prompt():
    while True:
        line = input("$ : ")

        if line == ".exit":
            break

        run(line)


def run_file(filename: str):
    with open(filename, "r") as contents:
        run(contents.read())


def main(argc: int, argv: List[str]):
    if argc > 2:
        raise ExecError("Too many arguments")
    elif argc == 2:
        run_file(argv[1])
    else:
        run_prompt()


if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
