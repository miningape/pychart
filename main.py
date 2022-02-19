from scanner import Scanner

if __name__ == "__main__":
    program = f""  # "1 + (2 / 3)"

    scanner = Scanner(program)
    tokens = scanner.get_tokens()

    print(list(map(str, tokens)))
