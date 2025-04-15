"""Analyzer module for AetherScript.

This module provides semantic analysis, type checking, and other static analysis tools for AetherScript.
"""

from aetherscript.analyzer.type_checker import TypeChecker
from aetherscript.analyzer.semantic_analyzer import SemanticAnalyzer
from aetherscript.analyzer.symbols import Symbol, SymbolTable, FunctionSymbol, VariableSymbol

__all__ = [
    "TypeChecker", "SemanticAnalyzer", "Symbol", "SymbolTable",
    "FunctionSymbol", "VariableSymbol"
]
