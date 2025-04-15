"""Parser for AetherScript."""

from typing import List, Optional, Dict, Callable, Any, Union

from aetherscript.parser.lexer import Lexer, Token, TokenType
from aetherscript.parser.ast import (
    Node, Program, Statement, Expression, Identifier,
    IntegerLiteral, FloatLiteral, StringLiteral, BooleanLiteral,
    BinaryExpression, UnaryExpression, VariableDeclaration,
    Parameter, FunctionDeclaration, ReturnStatement,
    BlockStatement, IfStatement, WhileStatement, ForStatement,
    ExpressionStatement, CallExpression, AssignmentExpression,
    ArrayLiteral, IndexExpression
)


class ParseError(Exception):
    """Exception raised when a parsing error occurs."""

    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message
        super().__init__(f"Parse Error at line {token.line}, column {token.column}: {message}")


class Parser:
    """Parser for AetherScript."""

    def __init__(self, source: str):
        """Initialize the parser with source code."""
        self.lexer = Lexer(source)
        self.tokens = self.lexer.tokenize()
        self.current = 0
        self.errors: List[ParseError] = []

        # Initialize operator precedence
        self.precedence = {
            TokenType.EQUALS: 1,         # ==
            TokenType.NOT_EQUALS: 1,     # !=
            TokenType.LESS_THAN: 2,      # <
            TokenType.GREATER_THAN: 2,   # >
            TokenType.LESS_EQUAL: 2,     # <=
            TokenType.GREATER_EQUAL: 2,  # >=
            TokenType.PLUS: 3,           # +
            TokenType.MINUS: 3,          # -
            TokenType.MULTIPLY: 4,       # *
            TokenType.DIVIDE: 4,         # /
            TokenType.MODULO: 4,         # %
            TokenType.LPAREN: 5,         # (
            TokenType.LBRACKET: 5,       # [
            TokenType.DOT: 6,            # .
        }

    def parse(self) -> Program:
        """Parse the source code and return an AST."""
        statements: List[Statement] = []

        while not self.is_at_end():
            try:
                statements.append(self.declaration())
            except ParseError as error:
                self.errors.append(error)
                self.synchronize()

        return Program(statements)

    def declaration(self) -> Statement:
        """Parse a declaration statement."""
        # This would be implemented with the specific AetherScript syntax
        # Placeholder for demonstration
        return self.statement()

    def statement(self) -> Statement:
        """Parse a statement."""
        # This would be implemented with the specific AetherScript syntax
        # Placeholder for demonstration
        return self.expression_statement()

    def expression_statement(self) -> Statement:
        """Parse an expression statement."""
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after expression.")
        return ExpressionStatement(expr, expr.line, expr.column)

    def expression(self) -> Expression:
        """Parse an expression."""
        # This would be implemented with the specific AetherScript syntax
        # Placeholder for demonstration
        return self.primary()

    def primary(self) -> Expression:
        """Parse a primary expression."""
        token = self.peek()

        if token.type == TokenType.INTEGER:
            self.advance()
            return IntegerLiteral(int(token.value), token.line, token.column)
        elif token.type == TokenType.FLOAT:
            self.advance()
            return FloatLiteral(float(token.value), token.line, token.column)
        elif token.type == TokenType.STRING:
            self.advance()
            return StringLiteral(token.value, token.line, token.column)
        elif token.type == TokenType.IDENTIFIER:
            self.advance()
            return Identifier(token.value, token.line, token.column)
        elif token.type == TokenType.LPAREN:
            self.advance()
            expr = self.expression()
            self.consume(TokenType.RPAREN, "Expected ')' after expression.")
            return expr

        # Error case
        self.advance()
        raise ParseError(token, f"Unexpected token: {token.value}")

    # Helper methods

    def peek(self) -> Token:
        """Return the current token without consuming it."""
        return self.tokens[self.current]

    def previous(self) -> Token:
        """Return the previously consumed token."""
        return self.tokens[self.current - 1]

    def is_at_end(self) -> bool:
        """Check if we've reached the end of the token stream."""
        return self.peek().type == TokenType.EOF

    def advance(self) -> Token:
        """Consume the current token and return it."""
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def consume(self, type: TokenType, message: str) -> Token:
        """Consume a token of the given type or raise an error."""
        if self.check(type):
            return self.advance()

        raise ParseError(self.peek(), message)

    def check(self, type: TokenType) -> bool:
        """Check if the current token is of the given type."""
        if self.is_at_end():
            return False
        return self.peek().type == type

    def match(self, *types: TokenType) -> bool:
        """Check if the current token matches any of the given types and advance if so."""
        for type in types:
            if self.check(type):
                self.advance()
                return True

        return False

    def synchronize(self) -> None:
        """Recover from a parse error by advancing to the next statement."""
        self.advance()

        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return

            if self.peek().type in (
                TokenType.FUNCTION,
                TokenType.SPELL,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.FOR,
                TokenType.RETURN
            ):
                return

            self.advance()
