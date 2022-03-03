from src.scanner import Scanner
from src.pyparser import Parser
from src import errors


def run(source: str):
    try:
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
        print(value)
    except errors.BaseError as e:
        print(e)


def run_prompt():
    try:
        while True:
            line = input("$ : ")

            if line == ".exit":
                break

            run(line)
    except KeyboardInterrupt:
        print()
        exit()


def run_file(filename: str):
    with open(filename, "r", encoding="utf-8") as contents:
        run(contents.read())
