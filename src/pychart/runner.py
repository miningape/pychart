from src.scanner import Scanner
from src.pyparser import Parser


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
    print(value)


def run_prompt():
    while True:
        line = input("$ : ")

        if line == ".exit":
            break

        run(line)


def run_file(filename: str):
    with open(filename, "r", encoding="utf-8") as contents:
        run(contents.read())
