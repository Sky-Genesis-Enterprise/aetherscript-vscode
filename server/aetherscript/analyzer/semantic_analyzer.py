"""Semantic analyzer for AetherScript.

This module provides functionality for finding definitions, references, and semantic information.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Union, Tuple

from aetherscript.parser.ast import (
    Node, Program, Statement, Expression, Identifier,
    FunctionDeclaration, VariableDeclaration, Parameter,
    CallExpression, AssignmentExpression, ASTVisitor
)
from aetherscript.analyzer.symbols import SymbolTable, Symbol, VariableSymbol, FunctionSymbol


@dataclass
class Location:
    """Represents a location in the source code."""

    line: int
    column: int

    def __str__(self) -> str:
        return f"{self.line}:{self.column}"


@dataclass
class Definition:
    """Represents a definition of a symbol."""

    name: str
    kind: str  # "variable", "function", "parameter", etc.
    location: Location
    type_name: str = ""
    detail: str = ""


@dataclass
class Reference:
    """Represents a reference to a symbol."""

    name: str
    location: Location
    definition: Definition


@dataclass
class SemanticInfo:
    """Contains semantic information for a source file."""

    definitions: Dict[str, List[Definition]] = field(default_factory=dict)
    references: List[Reference] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class SemanticAnalyzer(ASTVisitor):
    """Analyzes the semantics of AetherScript code."""

    def __init__(self):
        """Initialize the semantic analyzer."""
        self.symbol_table = SymbolTable()
        self.definitions: Dict[str, List[Definition]] = {}
        self.references: List[Reference] = []
        self.errors: List[str] = []
        self.current_function: Optional[FunctionSymbol] = None

        # Initialize with built-in functions and types
        self._init_builtins()

    def _init_builtins(self) -> None:
        """Initialize built-in functions and variables."""
        # Add built-in function symbols
        print_func = FunctionSymbol(
            name="print",
            type_name="Void",
            parameters=[VariableSymbol(name="value", type_name="Any")],
            is_builtin=True
        )
        self.symbol_table.define(print_func)

        # Record the definition
        self._record_definition(
            name="print",
            kind="function",
            location=Location(0, 0),
            type_name="Void",
            detail="Built-in function: print(value: Any) -> Void"
        )

    def analyze(self, program: Program) -> SemanticInfo:
        """Analyze the program and collect semantic information."""
        program.accept(self)
        return SemanticInfo(
            definitions=self.definitions,
            references=self.references,
            errors=self.errors
        )

    def find_definition(self, name: str, location: Location) -> Optional[Definition]:
        """Find the definition of a symbol at a given location."""
        # Find the definition that best matches the location
        definitions = self.definitions.get(name, [])
        if not definitions:
            return None

        # For now, just return the first definition
        # In a real implementation, we would check scopes
        return definitions[0]

    def find_all_references(self, name: str, def_location: Location) -> List[Reference]:
        """Find all references to a symbol."""
        # Filter references by name and definition location
        return [
            ref for ref in self.references
            if ref.name == name and (
                ref.definition.location.line == def_location.line and
                ref.definition.location.column == def_location.column
            )
        ]

    def find_hover_info(self, name: str, location: Location) -> Optional[str]:
        """Get hover information for a symbol at a given location."""
        # Find the definition
        definition = self.find_definition(name, location)
        if definition is None:
            return None

        # Format hover information
        if definition.detail:
            return f"{definition.kind} {definition.name}: {definition.type_name}\n{definition.detail}"
        else:
            return f"{definition.kind} {definition.name}: {definition.type_name}"

    def _record_definition(self, name: str, kind: str, location: Location, type_name: str = "", detail: str = "") -> Definition:
        """Record a definition."""
        definition = Definition(
            name=name,
            kind=kind,
            location=location,
            type_name=type_name,
            detail=detail
        )

        if name not in self.definitions:
            self.definitions[name] = []

        self.definitions[name].append(definition)
        return definition

    def _record_reference(self, name: str, location: Location, definition: Definition) -> Reference:
        """Record a reference."""
        reference = Reference(
            name=name,
            location=location,
            definition=definition
        )

        self.references.append(reference)
        return reference

    # ASTVisitor methods

    def visit_program(self, node: Program) -> Any:
        """Visit a program node."""
        for statement in node.statements:
            statement.accept(self)
        return None

    def visit_identifier(self, node: Identifier) -> Any:
        """Visit an identifier node."""
        # Look up the symbol
        symbol = self.symbol_table.resolve(node.name)

        if symbol is None:
            self.errors.append(f"Undefined identifier '{node.name}' at {node.line}:{node.column}")
            return None

        # Find the definition
        definition = self.find_definition(node.name, Location(node.line, node.column))

        if definition is not None:
            # Record a reference
            self._record_reference(
                name=node.name,
                location=Location(node.line, node.column),
                definition=definition
            )

        return None

    def visit_function_declaration(self, node: FunctionDeclaration) -> Any:
        """Visit a function declaration node."""
        # Record the function definition
        func_def = self._record_definition(
            name=node.name.name,
            kind="function",
            location=Location(node.line, node.column),
            type_name=node.return_type,
            detail=self._format_function_signature(node)
        )

        # Create a function symbol
        func_symbol = FunctionSymbol(
            name=node.name.name,
            type_name=node.return_type,
            parameters=[]
        )

        # Add the function to the current scope
        if self.symbol_table.contains_local(node.name.name):
            self.errors.append(f"Function '{node.name.name}' is already defined at {node.line}:{node.column}")
        else:
            self.symbol_table.define(func_symbol)

        # Create a new scope for the function body
        function_scope = self.symbol_table.create_child_scope(node.name.name)
        previous_scope = self.symbol_table
        self.symbol_table = function_scope

        # Save previous function and set current function
        previous_function = self.current_function
        self.current_function = func_symbol

        # Process parameters
        for param in node.parameters:
            param.accept(self)
            param_symbol = self.symbol_table.resolve_local(param.name.name)
            if param_symbol:
                func_symbol.parameters.append(param_symbol)

        # Process the function body
        for statement in node.body:
            statement.accept(self)

        # Restore previous scope and function
        self.symbol_table = previous_scope
        self.current_function = previous_function

        return None

    def visit_parameter(self, node: Parameter) -> Any:
        """Visit a parameter node."""
        # Record the parameter definition
        param_def = self._record_definition(
            name=node.name.name,
            kind="parameter",
            location=Location(node.name.line, node.name.column),
            type_name=node.type_annotation
        )

        # Create a parameter symbol
        param_symbol = VariableSymbol(
            name=node.name.name,
            type_name=node.type_annotation
        )

        # Add the parameter to the current scope
        self.symbol_table.define(param_symbol)

        return None

    def visit_variable_declaration(self, node: VariableDeclaration) -> Any:
        """Visit a variable declaration node."""
        # Determine variable type
        var_type = node.type_annotation or "inferred"

        # Record the variable definition
        var_def = self._record_definition(
            name=node.name.name,
            kind="variable",
            location=Location(node.line, node.column),
            type_name=var_type
        )

        # Create a variable symbol
        var_symbol = VariableSymbol(
            name=node.name.name,
            type_name=var_type
        )

        # Add the variable to the current scope
        if self.symbol_table.contains_local(node.name.name):
            self.errors.append(f"Variable '{node.name.name}' is already defined at {node.line}:{node.column}")
        else:
            self.symbol_table.define(var_symbol)

        # Process the initializer, if any
        if node.initializer is not None:
            node.initializer.accept(self)

        return None

    def visit_call_expression(self, node: CallExpression) -> Any:
        """Visit a call expression node."""
        # Process the callee
        node.callee.accept(self)

        # Process the arguments
        for arg in node.arguments:
            arg.accept(self)

        return None

    def visit_assignment_expression(self, node: AssignmentExpression) -> Any:
        """Visit an assignment expression node."""
        # Process the target
        node.target.accept(self)

        # Process the value
        node.value.accept(self)

        return None

    # Default implementation for other node types

    def visit_integer_literal(self, node: Any) -> Any:
        return None

    def visit_float_literal(self, node: Any) -> Any:
        return None

    def visit_string_literal(self, node: Any) -> Any:
        return None

    def visit_boolean_literal(self, node: Any) -> Any:
        return None

    def visit_binary_expression(self, node: Any) -> Any:
        node.left.accept(self)
        node.right.accept(self)
        return None

    def visit_unary_expression(self, node: Any) -> Any:
        node.right.accept(self)
        return None

    def visit_return_statement(self, node: Any) -> Any:
        if node.value is not None:
            node.value.accept(self)
        return None

    def visit_block_statement(self, node: Any) -> Any:
        # Create a new scope for the block
        block_scope = self.symbol_table.create_child_scope()
        previous_scope = self.symbol_table
        self.symbol_table = block_scope

        # Process the statements in the block
        for statement in node.statements:
            statement.accept(self)

        # Restore the previous scope
        self.symbol_table = previous_scope
        return None

    def visit_if_statement(self, node: Any) -> Any:
        node.condition.accept(self)
        node.then_branch.accept(self)
        if node.else_branch is not None:
            node.else_branch.accept(self)
        return None

    def visit_while_statement(self, node: Any) -> Any:
        node.condition.accept(self)
        node.body.accept(self)
        return None

    def visit_for_statement(self, node: Any) -> Any:
        # Create a new scope for the for loop
        for_scope = self.symbol_table.create_child_scope()
        previous_scope = self.symbol_table
        self.symbol_table = for_scope

        # Process the initializer, condition, and increment
        if node.initializer is not None:
            node.initializer.accept(self)

        if node.condition is not None:
            node.condition.accept(self)

        if node.increment is not None:
            node.increment.accept(self)

        # Process the body
        node.body.accept(self)

        # Restore the previous scope
        self.symbol_table = previous_scope
        return None

    def visit_expression_statement(self, node: Any) -> Any:
        node.expression.accept(self)
        return None

    def visit_array_literal(self, node: Any) -> Any:
        for element in node.elements:
            element.accept(self)
        return None

    def visit_index_expression(self, node: Any) -> Any:
        node.array.accept(self)
        node.index.accept(self)
        return None

    # Utility methods

    def _format_function_signature(self, node: FunctionDeclaration) -> str:
        """Format a function signature for documentation."""
        params = []
        for param in node.parameters:
            params.append(f"{param.name.name}: {param.type_annotation}")

        return f"function {node.name.name}({', '.join(params)}) -> {node.return_type}"
