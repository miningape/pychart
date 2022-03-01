from src.scanner import Scanner
from src.pyparser import Parser
from src import errors


def run(source: str):
    value = None
    try:
        scanner = Scanner(source)
        tokens = scanner.get_tokens()
        ast = Parser(tokens).parse()

        if ast is None:
            return

        value = ast()

        value = int(value)
    except errors.BaseError as e:
        errors.handler.handle_error(e)
    finally:
        # print(f"AST: {ast}")
        print(f'value: {value}')


def run_prompt():
    while True:
        line = input("$ : ")

        if line == ".exit":
            break

        run(line)


def run_file(filename: str):
    with open(filename, "r", encoding="utf-8") as contents:
        run(contents.read())
