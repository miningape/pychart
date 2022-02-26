from src.scanner import Scanner
from src.errors import Error


def run(source: str) -> Error:
    scanner = Scanner(source)
    tokens = scanner.get_tokens()

    # print(f"AST: {ast}")
    print(list(map(str, tokens)))


def run_prompt():
    count = 0
    while True:
        line = input(f"${count} : ")
        count += 1
        if line == ".exit":
            break

        error = run(line)
        if error:
            print(error)


def run_file(filename: str):
    with open(filename, "r", encoding="utf-8") as contents:
        run(contents.read())
