from src.pychart.scanner import Scanner
from src.pychart.token_type import TokenType


def test_scanner_int():
    scanner = Scanner("10")
    tokens = scanner.get_tokens()
    assert tokens[0].token_type == TokenType.NUMBER
    assert tokens[1].token_type == TokenType.EOF


def test_scanner_float():
    scanner = Scanner("1.23")
    tokens = scanner.get_tokens()
    assert tokens[0].token_type == TokenType.NUMBER
    assert tokens[1].token_type == TokenType.EOF
