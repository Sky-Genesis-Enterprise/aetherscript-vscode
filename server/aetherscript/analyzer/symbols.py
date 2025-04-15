"""Symbol handling for AetherScript."""

from abc import ABC
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set


@dataclass
class Symbol(ABC):
    """Base class for all symbols."""

    name: str
    type_name: str

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name}: {self.type_name})"


@dataclass
class VariableSymbol(Symbol):
    """Symbol representing a variable."""

    is_mutable: bool = True


@dataclass
class FunctionSymbol(Symbol):
    """Symbol representing a function."""

    parameters: List[Symbol] = field(default_factory=list)
    is_builtin: bool = False


@dataclass
class SymbolTable:
    """Symbol table for tracking declarations and scopes."""

    symbols: Dict[str, Symbol] = field(default_factory=dict)
    parent: Optional['SymbolTable'] = None
    name: str = "global"

    def define(self, symbol: Symbol) -> Symbol:
        """Define a new symbol in the current scope."""
        self.symbols[symbol.name] = symbol
        return symbol

    def resolve(self, name: str) -> Optional[Symbol]:
        """Look up a symbol by name, checking parent scopes if necessary."""
        symbol = self.symbols.get(name)

        if symbol is not None:
            return symbol

        if self.parent is not None:
            return self.parent.resolve(name)

        return None

    def resolve_local(self, name: str) -> Optional[Symbol]:
        """Look up a symbol by name in the current scope only."""
        return self.symbols.get(name)

    def contains(self, name: str) -> bool:
        """Check if the symbol exists in any accessible scope."""
        return self.resolve(name) is not None

    def contains_local(self, name: str) -> bool:
        """Check if the symbol exists in the current scope."""
        return name in self.symbols

    def create_child_scope(self, name: str = "") -> 'SymbolTable':
        """Create a new child scope."""
        scope_name = name if name else f"{self.name}.child{len(self.symbols)}"
        return SymbolTable(parent=self, name=scope_name)

    def __str__(self) -> str:
        return f"SymbolTable({self.name}, {len(self.symbols)} symbols)"
