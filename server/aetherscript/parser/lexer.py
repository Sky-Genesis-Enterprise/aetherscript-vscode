"""Lexer for AetherScript."""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    """Token types for AetherScript."""

    # Special tokens
    EOF = auto()
    ERROR = auto()

    # Literals
    IDENTIFIER = auto()
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()

    # Keywords
    IF = auto()
    ELSE = auto()
    ELIF = auto()
    WHILE = auto()
    FOR = auto()
    RETURN = auto()
    BREAK = auto()
    CONTINUE = auto()
    FUNCTION = auto()
    SPELL = auto()
    RITUAL = auto()
    CONJURE = auto()
    ENTITY = auto()
    REALM = auto()
    DIMENSION = auto()

    # Types
    VOID = auto()
    INT = auto()
    FLOAT_TYPE = auto()
    STRING_TYPE = auto()
    BOOLEAN = auto()
    ARRAY = auto()
    MAP = auto()
    ELEMENT = auto()
    ENERGY = auto()
    SPIRIT = auto()
    MATTER = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()
    ASSIGN = auto()
    EQUALS = auto()
    NOT_EQUALS = auto()
    LESS_THAN = auto()
    GREATER_THAN = auto()
    LESS_EQUAL = auto()
    GREATER_EQUAL = auto()
    AND = auto()
    OR = auto()
    NOT = auto()

    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    DOT = auto()
    SEMICOLON = auto()
    COLON = auto()


@dataclass
class Token:
    """Token representation."""

    type: TokenType
    value: str
    line: int
    column: int

    def __repr__(self) -> str:
        return f"Token({self.type}, '{self.value}', {self.line}:{self.column})"


class Lexer:
    """Lexer for AetherScript."""

    def __init__(self, source: str):
        """Initialize lexer with source code."""
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.current_char = self.source[0] if self.source else None

        # Keywords mapping
        self.keywords = {
            "if": TokenType.IF,
            "else": TokenType.ELSE,
            "elif": TokenType.ELIF,
            "while": TokenType.WHILE,
            "for": TokenType.FOR,
            "return": TokenType.RETURN,
            "break": TokenType.BREAK,
            "continue": TokenType.CONTINUE,
            "function": TokenType.FUNCTION,
            "spell": TokenType.SPELL,
            "ritual": TokenType.RITUAL,
            "conjure": TokenType.CONJURE,
            "entity": TokenType.ENTITY,
            "realm": TokenType.REALM,
            "dimension": TokenType.DIMENSION,
            "Void": TokenType.VOID,
            "Int": TokenType.INT,
            "Float": TokenType.FLOAT_TYPE,
            "String": TokenType.STRING_TYPE,
            "Boolean": TokenType.BOOLEAN,
            "Array": TokenType.ARRAY,
            "Map": TokenType.MAP,
            "Element": TokenType.ELEMENT,
            "Energy": TokenType.ENERGY,
            "Spirit": TokenType.SPIRIT,
            "Matter": TokenType.MATTER,
        }

    def advance(self) -> None:
        """Move to the next character."""
        self.position += 1

        if self.current_char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        self.current_char = self.source[self.position] if self.position < len(self.source) else None

    def skip_whitespace(self) -> None:
        """Skip whitespace characters."""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comment(self) -> None:
        """Skip comments."""
        if self.current_char == '/' and self.peek() == '/':
            # Line comment
            while self.current_char is not None and self.current_char != '\n':
                self.advance()
        elif self.current_char == '/' and self.peek() == '*':
            # Block comment
            self.advance()  # Skip '/'
            self.advance()  # Skip '*'

            while self.current_char is not None:
                if self.current_char == '*' and self.peek() == '/':
                    self.advance()  # Skip '*'
                    self.advance()  # Skip '/'
                    break
                self.advance()

    def peek(self) -> Optional[str]:
        """Look at the next character without advancing."""
        peek_pos = self.position + 1
        return self.source[peek_pos] if peek_pos < len(self.source) else None

    def tokenize(self) -> List[Token]:
        """Tokenize the source code."""
        tokens = []

        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == '/' and (self.peek() == '/' or self.peek() == '*'):
                self.skip_comment()
                continue

            # Identify tokens
            if self.current_char.isalpha() or self.current_char == '_':
                tokens.append(self.identifier())
            elif self.current_char.isdigit():
                tokens.append(self.number())
            elif self.current_char == '"' or self.current_char == "'":
                tokens.append(self.string())
            elif self.current_char == '+':
                tokens.append(Token(TokenType.PLUS, '+', self.line, self.column))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TokenType.MINUS, '-', self.line, self.column))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TokenType.MULTIPLY, '*', self.line, self.column))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TokenType.DIVIDE, '/', self.line, self.column))
                self.advance()
            elif self.current_char == '%':
                tokens.append(Token(TokenType.MODULO, '%', self.line, self.column))
                self.advance()
            elif self.current_char == '=':
                if self.peek() == '=':
                    token = Token(TokenType.EQUALS, '==', self.line, self.column)
                    self.advance()
                    self.advance()
                else:
                    token = Token(TokenType.ASSIGN, '=', self.line, self.column)
                    self.advance()
                tokens.append(token)
            elif self.current_char == '!':
                if self.peek() == '=':
                    token = Token(TokenType.NOT_EQUALS, '!=', self.line, self.column)
                    self.advance()
                    self.advance()
                else:
                    token = Token(TokenType.NOT, '!', self.line, self.column)
                    self.advance()
                tokens.append(token)
            elif self.current_char == '<':
                if self.peek() == '=':
                    token = Token(TokenType.LESS_EQUAL, '<=', self.line, self.column)
                    self.advance()
                    self.advance()
                else:
                    token = Token(TokenType.LESS_THAN, '<', self.line, self.column)
                    self.advance()
                tokens.append(token)
            elif self.current_char == '>':
                if self.peek() == '=':
                    token = Token(TokenType.GREATER_EQUAL, '>=', self.line, self.column)
                    self.advance()
                    self.advance()
                else:
                    token = Token(TokenType.GREATER_THAN, '>', self.line, self.column)
                    self.advance()
                tokens.append(token)
            elif self.current_char == '&' and self.peek() == '&':
                tokens.append(Token(TokenType.AND, '&&', self.line, self.column))
                self.advance()
                self.advance()
            elif self.current_char == '|' and self.peek() == '|':
                tokens.append(Token(TokenType.OR, '||', self.line, self.column))
                self.advance()
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TokenType.LPAREN, '(', self.line, self.column))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TokenType.RPAREN, ')', self.line, self.column))
                self.advance()
            elif self.current_char == '{':
                tokens.append(Token(TokenType.LBRACE, '{', self.line, self.column))
                self.advance()
            elif self.current_char == '}':
                tokens.append(Token(TokenType.RBRACE, '}', self.line, self.column))
                self.advance()
            elif self.current_char == '[':
                tokens.append(Token(TokenType.LBRACKET, '[', self.line, self.column))
                self.advance()
            elif self.current_char == ']':
                tokens.append(Token(TokenType.RBRACKET, ']', self.line, self.column))
                self.advance()
            elif self.current_char == ',':
                tokens.append(Token(TokenType.COMMA, ',', self.line, self.column))
                self.advance()
            elif self.current_char == '.':
                tokens.append(Token(TokenType.DOT, '.', self.line, self.column))
                self.advance()
            elif self.current_char == ';':
                tokens.append(Token(TokenType.SEMICOLON, ';', self.line, self.column))
                self.advance()
            elif self.current_char == ':':
                tokens.append(Token(TokenType.COLON, ':', self.line, self.column))
                self.advance()
            else:
                # Unrecognized character
                tokens.append(Token(TokenType.ERROR, self.current_char, self.line, self.column))
                self.advance()

        # Add EOF token
        tokens.append(Token(TokenType.EOF, '', self.line, self.column))

        return tokens

    def identifier(self) -> Token:
        """Process identifiers and keywords."""
        line, column = self.line, self.column
        result = ""

        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()

        # Check if the identifier is a keyword
        token_type = self.keywords.get(result, TokenType.IDENTIFIER)

        return Token(token_type, result, line, column)

    def number(self) -> Token:
        """Process numeric literals."""
        line, column = self.line, self.column
        result = ""
        is_float = False

        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                # Cannot have more than one decimal point
                if is_float:
                    break
                is_float = True

            result += self.current_char
            self.advance()

        # Handle case like "123." which should be "123.0"
        if result.endswith('.'):
            result += '0'

        token_type = TokenType.FLOAT if is_float else TokenType.INTEGER

        return Token(token_type, result, line, column)

    def string(self) -> Token:
        """Process string literals."""
        line, column = self.line, self.column
        quote = self.current_char  # Save the quote character (' or ")
        self.advance()  # Skip the opening quote

        result = ""

        while self.current_char is not None and self.current_char != quote:
            # Handle escape sequences
            if self.current_char == '\\' and self.peek() is not None:
                self.advance()  # Skip backslash

                # Process escape sequence
                escape_map = {
                    'n': '\n',
                    't': '\t',
                    'r': '\r',
                    '\\': '\\',
                    '"': '"',
                    "'": "'"
                }

                result += escape_map.get(self.current_char, self.current_char)
            else:
                result += self.current_char

            self.advance()

        if self.current_char is None:
            # Unterminated string
            return Token(TokenType.ERROR, result, line, column)

        self.advance()  # Skip the closing quote

        return Token(TokenType.STRING, result, line, column)
