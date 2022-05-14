from typing import List, Optional
from src.pychart._interpreter.token_type import Token, TokenType
from src.pychart._interpreter.ast_nodes.statement import (
    Block,
    Break,
    Expression,
    Function,
    If,
    Print,
    Stmt,
    Let,
    While,
)
from src.pychart._interpreter.ast_nodes.expression import (
    Array,
    Assignment,
    Binary,
    Call,
    Index,
    Unary,
    Grouping,
    Expr,
    Literal,
    Variable,
)


class Parser:
    tokens: List[Token] = []
    current: int = 0

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens

    def parse(self):
        statements: List[Stmt] = []

        try:
            while not self.is_at_end():
                statements.append(self.declaration())
        except RuntimeError as err:
            print("Error occurred", err)
            return None

        return statements

    def declaration(self) -> Stmt:
        if self.match(TokenType.LET):
            return self.var_declaration()

        return self.statement()

    def var_declaration(self) -> Stmt:
        name = self.consume(TokenType.IDENTIFIER, "Expected a variable name")

        initializer: Optional[Expr] = None

        if self.match(TokenType.EQUAL):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, 'Expected ";" after variable declaration')
        return Let(name, initializer)

    def statement(self) -> Stmt:
        # if self.match(TokenType.PRINT):
        # return self.print_statement()
        if self.match(TokenType.FUNCTION):
            return self.function()
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.LEFT_BRACE):
            return Block(self.block())
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.BREAK):
            return self.break_statement()

        return self.expression_statement()

    def expression_statement(self) -> Stmt:
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, 'Expected ";" after expression')
        return Expression(expr)

    def break_statement(self) -> Stmt:
        self.consume(TokenType.SEMICOLON, 'Expected ";" after expression')
        return Break()

    def while_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PEREN, 'Expected "(" after WHILE keyword')
        while_test = self.expression()
        self.consume(
            TokenType.RIGHT_PEREN, 'Expected ")" after expression in WHILE statement'
        )

        while_body = self.statement()

        return While(while_test, while_body)

    def if_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PEREN, 'Expected "(" after IF keyword')
        if_test = self.expression()
        self.consume(
            TokenType.RIGHT_PEREN, 'Expected ")" after expression in IF statement'
        )

        if_body = self.statement()
        else_body = None

        matched_elif = False
        if self.match(TokenType.ELIF):
            matched_elif = True
            else_body = self.if_statement()

        if self.match(TokenType.ELSE):
            if matched_elif:
                raise RuntimeError("Only 1 ELSE can be after an IF")
            else_body = self.statement()

        return If(if_test, if_body, else_body)

    def print_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PEREN, 'Expected "(" after PRINT keyword')
        expr = self.expression()
        self.consume(
            TokenType.RIGHT_PEREN, 'Expected ")" after expression in print call'
        )
        self.consume(TokenType.SEMICOLON, 'Expected ";" after expression')
        return Print(expr)

    def function(self) -> Stmt:
        name = self.consume(
            TokenType.IDENTIFIER, "Expected Identifier after FUNC keyword"
        )
        self.consume(TokenType.LEFT_PEREN, 'Expected "(" after FUNC Identifier')

        params: List[Token] = []
        if not self.check(TokenType.RIGHT_PEREN):
            params.append(
                self.consume(TokenType.IDENTIFIER, "Expected identifier in arg list")
            )

            while self.match(TokenType.COMMA):
                if len(params) > 127:
                    self.error(self.peek(), "Too many arguments for function, max 127")

                params.append(
                    self.consume(
                        TokenType.IDENTIFIER, "Expected identifier in arg list"
                    )
                )

        self.consume(TokenType.RIGHT_PEREN, 'Expected ")" after argument list')
        self.consume(
            TokenType.LEFT_BRACE, 'Expected "{" after arg list in FUNC declaration'
        )
        body = self.block()

        return Function(name, params, body)

    def block(self) -> List[Stmt]:
        statements: List[Stmt] = []

        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())

        self.consume(TokenType.RIGHT_BRACE, 'Expected "}" after block')

        return statements

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def peek(self) -> Token:
        return self.tokens[self.current]

    def is_at_end(self):
        return self.peek().token_type == TokenType.EOF

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def check(self, token: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.tokens[self.current].token_type == token

    def match(self, *tokens_to_match: TokenType) -> bool:
        for token in tokens_to_match:
            if self.check(token):
                self.advance()
                return True

        return False

    def consume(self, type_: TokenType, message: str) -> Token:
        if self.check(type_):
            return self.advance()

        self.error(self.peek(), message)

    def error(self, token: Token, message: str):
        if token.token_type == TokenType.EOF:
            print(f"At end of line: {message}")
        else:
            print(f"Line {token.line}, unable to match. {message}")
        raise RuntimeError()

    def expression(self) -> Expr:
        return self.assignment()

    def assignment(self) -> Expr:
        expr = self.equality()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, Variable):
                return Assignment(expr.name, value)

            self.error(equals, "Could not assign target")

        return expr

    def equality(self) -> Expr:
        expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()

            expr = Binary(expr, operator, right)

        return expr

    def comparison(self) -> Expr:
        expr = self.term()

        while self.match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESSER,
            TokenType.LESSER_EQUAL,
        ):
            operator = self.previous()
            right = self.term()

            expr = Binary(expr, operator, right)

        return expr

    def term(self) -> Expr:
        expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()

            expr = Binary(expr, operator, right)

        return expr

    def factor(self) -> Expr:
        expr = self.unary()

        while self.match(TokenType.STAR, TokenType.SLASH):
            operator = self.previous()
            right = self.unary()

            expr = Binary(expr, operator, right)

        return expr

    def unary(self) -> Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()

            return Unary(operator, right)

        return self.index()

    def index(self) -> Expr:
        expr = self.call()

        while True:
            if self.match(TokenType.LEFT_BRACK):
                index = self.expression()

                self.consume(TokenType.RIGHT_BRACK, "Expected ']' following expression")

                expr = Index(expr, index)
            else:
                break

        return expr

    def call(self) -> Expr:
        expr = self.primary()

        while True:
            if self.match(TokenType.LEFT_PEREN):
                expr = self.finish_call(expr)
            else:
                break

        return expr

    def finish_call(self, callee: Expr) -> Expr:
        args: List[Expr] = []

        if not self.check(TokenType.RIGHT_PEREN):
            args.append(self.expression())

            while self.match(TokenType.COMMA):
                if len(args) > 127:
                    self.error(self.peek(), "Too many arguments in function, max 127")
                args.append(self.expression())

        self.consume(TokenType.RIGHT_PEREN, 'Expected ")" after function arguments.')

        return Call(callee, args)

    def primary(self) -> Expr:
        if self.match(TokenType.FALSE):
            return Literal(False)
        if self.match(TokenType.TRUE):
            return Literal(True)
        if self.match(TokenType.NULL):
            return Literal(None)

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)

        if self.match(TokenType.LEFT_PEREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PEREN, "Cannot match )")
            return Grouping(expr)

        if self.match(TokenType.LEFT_BRACK):
            elems: List[Expr] = []
            if not self.check(TokenType.RIGHT_BRACK):
                elems.append(self.expression())

                while self.match(TokenType.COMMA):
                    elems.append(self.expression())

            self.consume(TokenType.RIGHT_BRACK, "Expected ']' following '['")
            return Array(elems)

        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())

        self.error(self.peek(), "Could not match to an expression")
