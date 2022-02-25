from shutil import ExecError
import sys
from typing import List
from pyparser import Parser

from libs.scanner import Scanner


def run(source: str):
    scanner = Scanner(source)
    tokens = scanner.get_tokens()
    ast = Parser(tokens).parse()

    if ast is None:
        return

    value = ast()

    try:
        value = int(value)
    except:                                                                                                                                                                         
        pass

    # print(f"AST: {ast}")
    print(f": $ {value}")


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
