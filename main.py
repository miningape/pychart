from scanner import Scanner

if __name__ == "__main__":
    program = "() >= >>==="  # "1 + (2 / 3)"

    scanner = Scanner("10")
    tokens = scanner.get_tokens()

    print(list(map(str, tokens)))
