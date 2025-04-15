"""Type checker for AetherScript."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Set, Tuple

from aetherscript.parser.ast import (
    Program, Node, Statement, Expression, Identifier,
    IntegerLiteral, FloatLiteral, StringLiteral, BooleanLiteral,
    BinaryExpression, UnaryExpression, VariableDeclaration,
    Parameter, FunctionDeclaration, ReturnStatement,
    BlockStatement, IfStatement, WhileStatement, ForStatement,
    ExpressionStatement, CallExpression, AssignmentExpression,
    ArrayLiteral, IndexExpression, ASTVisitor
)
from aetherscript.analyzer.symbols import SymbolTable, Symbol, VariableSymbol, FunctionSymbol


@dataclass
class TypeError:
    """Represents a type error."""

    message: str
    line: int
    column: int

    def __str__(self) -> str:
        return f"Type Error at line {self.line}, column {self.column}: {self.message}"


class TypeChecker(ASTVisitor):
    """Type checker for AetherScript."""

    def __init__(self):
        """Initialize the type checker."""
        self.symbol_table = SymbolTable()
        self.errors: List[TypeError] = []
        self.current_function: Optional[FunctionSymbol] = None

        # Define built-in types
        self.types = {
            "Void", "Int", "Float", "String", "Boolean",
            "Array", "Map", "Element", "Energy", "Spirit", "Matter"
        }

        # Initialize with built-in functions and variables
        self._init_builtins()

    def _init_builtins(self) -> None:
        """Initialize built-in functions and variables."""
        # Add built-in functions like print, etc.
        self.symbol_table.define(
            FunctionSymbol(
                name="print",
                type_name="Void",
                parameters=[VariableSymbol(name="value", type_name="Any")],
                is_builtin=True
            )
        )

    def check(self, program: Program) -> List[TypeError]:
        """Type check the program."""
        program.accept(self)
        return self.errors

    def visit_program(self, node: Program) -> Any:
        """Visit a program node."""
        for statement in node.statements:
            statement.accept(self)
        return "Program"

    def visit_identifier(self, node: Identifier) -> str:
        """Visit an identifier node."""
        symbol = self.symbol_table.resolve(node.name)

        if symbol is None:
            self.errors.append(
                TypeError(
                    message=f"Undefined identifier '{node.name}'",
                    line=node.line,
                    column=node.column
                )
            )
            return "Unknown"

        return symbol.type_name

    def visit_integer_literal(self, node: IntegerLiteral) -> str:
        """Visit an integer literal node."""
        return "Int"

    def visit_float_literal(self, node: FloatLiteral) -> str:
        """Visit a float literal node."""
        return "Float"

    def visit_string_literal(self, node: StringLiteral) -> str:
        """Visit a string literal node."""
        return "String"

    def visit_boolean_literal(self, node: BooleanLiteral) -> str:
        """Visit a boolean literal node."""
        return "Boolean"

    def visit_binary_expression(self, node: BinaryExpression) -> str:
        """Visit a binary expression node."""
        left_type = node.left.accept(self)
        right_type = node.right.accept(self)

        # Example type checking for binary operators
        if node.operator in ["+", "-", "*", "/"]:
            if left_type == "Int" and right_type == "Int":
                return "Int"
            elif left_type in ["Int", "Float"] and right_type in ["Int", "Float"]:
                return "Float"
            elif node.operator == "+" and (left_type == "String" or right_type == "String"):
                return "String"

        elif node.operator in ["==", "!=", "<", ">", "<=", ">="]:
            # Comparison operators
            return "Boolean"

        # Error case - incompatible types
        self.errors.append(
            TypeError(
                message=f"Cannot apply operator '{node.operator}' to types '{left_type}' and '{right_type}'",
                line=node.line,
                column=node.column
            )
        )
        return "Unknown"

    def visit_unary_expression(self, node: UnaryExpression) -> str:
        """Visit a unary expression node."""
        right_type = node.right.accept(self)

        # Example type checking for unary operators
        if node.operator == "-":
            if right_type in ["Int", "Float"]:
                return right_type
        elif node.operator == "!":
            if right_type == "Boolean":
                return "Boolean"

        # Error case
        self.errors.append(
            TypeError(
                message=f"Cannot apply unary operator '{node.operator}' to type '{right_type}'",
                line=node.line,
                column=node.column
            )
        )
        return "Unknown"

    def visit_variable_declaration(self, node: VariableDeclaration) -> Any:
        """Visit a variable declaration node."""
        # If there's an initializer, check its type
        init_type = "Void"
        if node.initializer is not None:
            init_type = node.initializer.accept(self)

        # If there's a type annotation, ensure the initializer matches
        if node.type_annotation is not None:
            if node.type_annotation not in self.types:
                self.errors.append(
                    TypeError(
                        message=f"Unknown type '{node.type_annotation}'",
                        line=node.line,
                        column=node.column
                    )
                )
            elif node.initializer is not None and init_type != node.type_annotation:
                self.errors.append(
                    TypeError(
                        message=f"Cannot assign a value of type '{init_type}' to a variable of type '{node.type_annotation}'",
                        line=node.line,
                        column=node.column
                    )
                )

        # Determine the final type (annotation or inferred)
        var_type = node.type_annotation if node.type_annotation is not None else init_type

        # Create a variable symbol and add it to the symbol table
        if self.symbol_table.contains_local(node.name.name):
            self.errors.append(
                TypeError(
                    message=f"Variable '{node.name.name}' is already defined in this scope",
                    line=node.line,
                    column=node.column
                )
            )
        else:
            self.symbol_table.define(
                VariableSymbol(
                    name=node.name.name,
                    type_name=var_type
                )
            )

        return None

    # Implement the remaining visitor methods for the ASTVisitor interface
    # For brevity, not all methods are implemented here

    def visit_function_declaration(self, node: FunctionDeclaration) -> Any:
        """Visit a function declaration node."""
        # Create a new function symbol
        func_symbol = FunctionSymbol(
            name=node.name.name,
            type_name=node.return_type,
            parameters=[]
        )

        # Add the function to the current scope
        if self.symbol_table.contains_local(node.name.name):
            self.errors.append(
                TypeError(
                    message=f"Function '{node.name.name}' is already defined in this scope",
                    line=node.line,
                    column=node.column
                )
            )
        else:
            self.symbol_table.define(func_symbol)

        # Create a new scope for the function body
        function_scope = self.symbol_table.create_child_scope(node.name.name)
        previous_scope = self.symbol_table
        self.symbol_table = function_scope

        # Save previous function and set current function
        previous_function = self.current_function
        self.current_function = func_symbol

        # Add parameters to the function scope
        for param in node.parameters:
            param_symbol = VariableSymbol(
                name=param.name.name,
                type_name=param.type_annotation
            )
            self.symbol_table.define(param_symbol)
            func_symbol.parameters.append(param_symbol)

        # Type check the function body
        for statement in node.body:
            statement.accept(self)

        # Restore previous scope and function
        self.symbol_table = previous_scope
        self.current_function = previous_function

        return None

    def visit_parameter(self, node: Parameter) -> Any:
        """Visit a parameter node."""
        # Parameters are handled in the function declaration
        return None

    def visit_return_statement(self, node: ReturnStatement) -> Any:
        """Visit a return statement node."""
        # Check if we're in a function
        if self.current_function is None:
            self.errors.append(
                TypeError(
                    message="Return statement outside of function",
                    line=node.line,
                    column=node.column
                )
            )
            return None

        # Check the return type
        if node.value is None:
            if self.current_function.type_name != "Void":
                self.errors.append(
                    TypeError(
                        message=f"Function '{self.current_function.name}' must return a value of type '{self.current_function.type_name}'",
                        line=node.line,
                        column=node.column
                    )
                )
        else:
            return_type = node.value.accept(self)
            if return_type != self.current_function.type_name:
                self.errors.append(
                    TypeError(
                        message=f"Cannot return a value of type '{return_type}' from a function with return type '{self.current_function.type_name}'",
                        line=node.line,
                        column=node.column
                    )
                )

        return None

    # Other visitor methods would be implemented similarly

    def visit_block_statement(self, node: BlockStatement) -> Any:
        """Visit a block statement node."""
        # Create a new scope for the block
        block_scope = self.symbol_table.create_child_scope()
        previous_scope = self.symbol_table
        self.symbol_table = block_scope

        # Type check the statements in the block
        for statement in node.statements:
            statement.accept(self)

        # Restore the previous scope
        self.symbol_table = previous_scope

        return None

    def visit_if_statement(self, node: IfStatement) -> Any:
        """Visit an if statement node."""
        # Check that the condition is a boolean
        condition_type = node.condition.accept(self)
        if condition_type != "Boolean":
            self.errors.append(
                TypeError(
                    message=f"If condition must be a Boolean, got '{condition_type}'",
                    line=node.condition.line,
                    column=node.condition.column
                )
            )

        # Type check the then and else branches
        node.then_branch.accept(self)
        if node.else_branch is not None:
            node.else_branch.accept(self)

        return None

    def visit_while_statement(self, node: WhileStatement) -> Any:
        """Visit a while statement node."""
        # Check that the condition is a boolean
        condition_type = node.condition.accept(self)
        if condition_type != "Boolean":
            self.errors.append(
                TypeError(
                    message=f"While condition must be a Boolean, got '{condition_type}'",
                    line=node.condition.line,
                    column=node.condition.column
                )
            )

        # Type check the body
        node.body.accept(self)

        return None

    def visit_for_statement(self, node: ForStatement) -> Any:
        """Visit a for statement node."""
        # Create a new scope for the for loop
        for_scope = self.symbol_table.create_child_scope()
        previous_scope = self.symbol_table
        self.symbol_table = for_scope

        # Type check the initializer, condition, and increment
        if node.initializer is not None:
            node.initializer.accept(self)

        if node.condition is not None:
            condition_type = node.condition.accept(self)
            if condition_type != "Boolean":
                self.errors.append(
                    TypeError(
                        message=f"For condition must be a Boolean, got '{condition_type}'",
                        line=node.condition.line,
                        column=node.condition.column
                    )
                )

        if node.increment is not None:
            node.increment.accept(self)

        # Type check the body
        node.body.accept(self)

        # Restore the previous scope
        self.symbol_table = previous_scope

        return None

    def visit_expression_statement(self, node: ExpressionStatement) -> Any:
        """Visit an expression statement node."""
        node.expression.accept(self)
        return None

    def visit_call_expression(self, node: CallExpression) -> str:
        """Visit a call expression node."""
        # Determine the type of the callee
        callee_type = node.callee.accept(self)

        # If it's a function call
        if isinstance(node.callee, Identifier):
            func_name = node.callee.name
            func_symbol = self.symbol_table.resolve(func_name)

            if func_symbol is None:
                self.errors.append(
                    TypeError(
                        message=f"Undefined function '{func_name}'",
                        line=node.line,
                        column=node.column
                    )
                )
                return "Unknown"

            # Check if it's callable
            if not isinstance(func_symbol, FunctionSymbol):
                self.errors.append(
                    TypeError(
                        message=f"Cannot call non-function '{func_name}'",
                        line=node.line,
                        column=node.column
                    )
                )
                return "Unknown"

            # Check the number of arguments
            if len(node.arguments) != len(func_symbol.parameters):
                self.errors.append(
                    TypeError(
                        message=f"Function '{func_name}' expects {len(func_symbol.parameters)} arguments, but got {len(node.arguments)}",
                        line=node.line,
                        column=node.column
                    )
                )
            else:
                # Check argument types
                for i, (arg, param) in enumerate(zip(node.arguments, func_symbol.parameters)):
                    arg_type = arg.accept(self)
                    if arg_type != param.type_name and param.type_name != "Any":
                        self.errors.append(
                            TypeError(
                                message=f"Argument {i+1} to function '{func_name}' must be of type '{param.type_name}', got '{arg_type}'",
                                line=arg.line if hasattr(arg, 'line') else node.line,
                                column=arg.column if hasattr(arg, 'column') else node.column
                            )
                        )

            return func_symbol.type_name

        # Error case
        self.errors.append(
            TypeError(
                message=f"Expression of type '{callee_type}' is not callable",
                line=node.line,
                column=node.column
            )
        )
        return "Unknown"

    def visit_assignment_expression(self, node: AssignmentExpression) -> str:
        """Visit an assignment expression node."""
        # Get the target variable type
        if isinstance(node.target, Identifier):
            var_name = node.target.name
            var_symbol = self.symbol_table.resolve(var_name)

            if var_symbol is None:
                self.errors.append(
                    TypeError(
                        message=f"Undefined variable '{var_name}'",
                        line=node.line,
                        column=node.column
                    )
                )
                return "Unknown"

            # Check if the variable is mutable
            if isinstance(var_symbol, VariableSymbol) and not var_symbol.is_mutable:
                self.errors.append(
                    TypeError(
                        message=f"Cannot assign to immutable variable '{var_name}'",
                        line=node.line,
                        column=node.column
                    )
                )

            # Check value type compatibility
            value_type = node.value.accept(self)
            if value_type != var_symbol.type_name:
                self.errors.append(
                    TypeError(
                        message=f"Cannot assign a value of type '{value_type}' to a variable of type '{var_symbol.type_name}'",
                        line=node.line,
                        column=node.column
                    )
                )

            return var_symbol.type_name

        # Error case
        self.errors.append(
            TypeError(
                message="Invalid assignment target",
                line=node.line,
                column=node.column
            )
        )
        return "Unknown"

    def visit_array_literal(self, node: ArrayLiteral) -> str:
        """Visit an array literal node."""
        if not node.elements:
            return "Array<Any>"

        # Determine the element type
        element_type = node.elements[0].accept(self)

        # Check that all elements have the same type
        for element in node.elements[1:]:
            current_type = element.accept(self)
            if current_type != element_type:
                self.errors.append(
                    TypeError(
                        message=f"Array elements must all have the same type. Expected '{element_type}', got '{current_type}'",
                        line=element.line if hasattr(element, 'line') else node.line,
                        column=element.column if hasattr(element, 'column') else node.column
                    )
                )

        return f"Array<{element_type}>"

    def visit_index_expression(self, node: IndexExpression) -> str:
        """Visit an index expression node."""
        array_type = node.array.accept(self)
        index_type = node.index.accept(self)

        # Check if the indexed object is an array
        if not array_type.startswith("Array<"):
            self.errors.append(
                TypeError(
                    message=f"Cannot index into non-array type '{array_type}'",
                    line=node.line,
                    column=node.column
                )
            )
            return "Unknown"

        # Check if the index is an integer
        if index_type != "Int":
            self.errors.append(
                TypeError(
                    message=f"Array index must be an Int, got '{index_type}'",
                    line=node.index.line if hasattr(node.index, 'line') else node.line,
                    column=node.index.column if hasattr(node.index, 'column') else node.column
                )
            )

        # Extract the element type from the array type (e.g., "Array<Int>" -> "Int")
        element_type = array_type[6:-1]
        return element_type
