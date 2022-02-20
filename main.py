from shutil import ExecError
import sys
from typing import List

from scanner import Scanner


def run(source: str):
    scanner = Scanner(source)
    tokens = scanner.get_tokens()

    print(list(map(str, tokens)))


def runPrompt():
    while True:
        line = input("$ : ")

        if line == ".exit":
            break

        run(line)


def runFile(filename: str):
    with open(filename, "r") as contents:
        run(contents.read())


def main(argc: int, argv: List[str]):
    if argc > 2:
        raise ExecError("Too many arguments")
    elif argc == 2:
        runFile(argv[1])
    else:
        runPrompt()


if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
