from shutil import ExecError
import sys
from os.path import dirname
from typing import List

sys.path.append('src')
from pychart.scanner import Scanner


def run(source: str):
    scanner = Scanner(source)
    tokens = scanner.get_tokens()

    print(list(map(str, tokens)))


def run_prompt():
    while True:
        line = input("$ : ")

        if line == ".exit":
            break

        run(line)


def run_file(filename: str):
    with open(filename, "r", encoding="utf-8") as contents:
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
