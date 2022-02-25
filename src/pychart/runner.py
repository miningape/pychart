from src.scanner import Scanner


def run(source: str):
    scanner = Scanner(source)
    tokens = scanner.get_tokens()

    # print(f"AST: {ast}")
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
