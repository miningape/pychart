from scanner import Scanner

if __name__ == "__main__":
    program = "1 + (2 / 3)"

    scanner = Scanner(program)
    tokens = scanner.getTokens()

    print(tokens)
