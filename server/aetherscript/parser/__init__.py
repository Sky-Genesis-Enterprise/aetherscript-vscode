"""Parser module for AetherScript."""

from aetherscript.parser.lexer import Lexer
from aetherscript.parser.ast import (
    Node, Program, Statement, Expression, FunctionDeclaration,
    IfStatement, WhileStatement, ReturnStatement
)
from aetherscript.parser.parser import Parser

__all__ = [
    "Lexer", "Parser", "Node", "Program", "Statement",
    "Expression", "FunctionDeclaration", "IfStatement",
    "WhileStatement", "ReturnStatement"
]
