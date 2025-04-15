"""Abstract Syntax Tree (AST) for AetherScript."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Any, Dict, Union


class Node(ABC):
    """Base class for all AST nodes."""

    @abstractmethod
    def accept(self, visitor: 'ASTVisitor') -> Any:
        """Accept a visitor to process this node."""
        pass


class Expression(Node):
    """Base class for all expressions."""
    pass


class Statement(Node):
    """Base class for all statements."""
    pass


@dataclass
class Program(Node):
    """Represents a complete program."""

    statements: List[Statement]

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_program(self)


@dataclass
class Identifier(Expression):
    """Represents an identifier."""

    name: str
    line: int
    column: int

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_identifier(self)


@dataclass
class Literal(Expression):
    """Base class for literal values."""

    value: Any
    line: int
    column: int


@dataclass
class IntegerLiteral(Literal):
    """Represents an integer literal."""

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_integer_literal(self)


@dataclass
class FloatLiteral(Literal):
    """Represents a float literal."""

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_float_literal(self)


@dataclass
class StringLiteral(Literal):
    """Represents a string literal."""

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_string_literal(self)


@dataclass
class BooleanLiteral(Literal):
    """Represents a boolean literal."""

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_boolean_literal(self)


@dataclass
class BinaryExpression(Expression):
    """Represents a binary operation."""

    left: Expression
    operator: str
    right: Expression
    line: int
    column: int

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_binary_expression(self)


@dataclass
class UnaryExpression(Expression):
    """Represents a unary operation."""

    operator: str
    right: Expression
    line: int
    column: int

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_unary_expression(self)


@dataclass
class VariableDeclaration(Statement):
    """Represents a variable declaration."""

    name: Identifier
    type_annotation: Optional[str]
    initializer: Optional[Expression]
    line: int
    column: int

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_variable_declaration(self)


@dataclass
class Parameter(Node):
    """Represents a function parameter."""

    name: Identifier
    type_annotation: str

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_parameter(self)


@dataclass
class FunctionDeclaration(Statement):
    """Represents a function declaration."""

    name: Identifier
    parameters: List[Parameter]
    return_type: str
    body: List[Statement]
    line: int
    column: int

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_function_declaration(self)


@dataclass
class ReturnStatement(Statement):
    """Represents a return statement."""

    value: Optional[Expression]
    line: int
    column: int

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_return_statement(self)


@dataclass
class BlockStatement(Statement):
    """Represents a block of statements."""

    statements: List[Statement]
    line: int
    column: int

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_block_statement(self)


@dataclass
class IfStatement(Statement):
    """Represents an if statement."""

    condition: Expression
    then_branch: Statement
    else_branch: Optional[Statement]
    line: int
    column: int

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_if_statement(self)


@dataclass
class WhileStatement(Statement):
    """Represents a while statement."""

    condition: Expression
    body: Statement
    line: int
    column: int

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_while_statement(self)


@dataclass
class ForStatement(Statement):
    """Represents a for statement."""

    initializer: Optional[Union[VariableDeclaration, Expression]]
    condition: Optional[Expression]
    increment: Optional[Expression]
    body: Statement
    line: int
    column: int

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_for_statement(self)


@dataclass
class ExpressionStatement(Statement):
    """Represents an expression used as a statement."""

    expression: Expression
    line: int
    column: int

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_expression_statement(self)


@dataclass
class CallExpression(Expression):
    """Represents a function call."""

    callee: Expression
    arguments: List[Expression]
    line: int
    column: int

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_call_expression(self)


@dataclass
class AssignmentExpression(Expression):
    """Represents an assignment."""

    target: Expression
    value: Expression
    line: int
    column: int

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_assignment_expression(self)


@dataclass
class ArrayLiteral(Expression):
    """Represents an array literal."""

    elements: List[Expression]
    line: int
    column: int

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_array_literal(self)


@dataclass
class IndexExpression(Expression):
    """Represents an array index operation."""

    array: Expression
    index: Expression
    line: int
    column: int

    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_index_expression(self)


class ASTVisitor(ABC):
    """Base visitor class for traversing the AST."""

    @abstractmethod
    def visit_program(self, node: Program) -> Any:
        pass

    @abstractmethod
    def visit_identifier(self, node: Identifier) -> Any:
        pass

    @abstractmethod
    def visit_integer_literal(self, node: IntegerLiteral) -> Any:
        pass

    @abstractmethod
    def visit_float_literal(self, node: FloatLiteral) -> Any:
        pass

    @abstractmethod
    def visit_string_literal(self, node: StringLiteral) -> Any:
        pass

    @abstractmethod
    def visit_boolean_literal(self, node: BooleanLiteral) -> Any:
        pass

    @abstractmethod
    def visit_binary_expression(self, node: BinaryExpression) -> Any:
        pass

    @abstractmethod
    def visit_unary_expression(self, node: UnaryExpression) -> Any:
        pass

    @abstractmethod
    def visit_variable_declaration(self, node: VariableDeclaration) -> Any:
        pass

    @abstractmethod
    def visit_parameter(self, node: Parameter) -> Any:
        pass

    @abstractmethod
    def visit_function_declaration(self, node: FunctionDeclaration) -> Any:
        pass

    @abstractmethod
    def visit_return_statement(self, node: ReturnStatement) -> Any:
        pass

    @abstractmethod
    def visit_block_statement(self, node: BlockStatement) -> Any:
        pass

    @abstractmethod
    def visit_if_statement(self, node: IfStatement) -> Any:
        pass

    @abstractmethod
    def visit_while_statement(self, node: WhileStatement) -> Any:
        pass

    @abstractmethod
    def visit_for_statement(self, node: ForStatement) -> Any:
        pass

    @abstractmethod
    def visit_expression_statement(self, node: ExpressionStatement) -> Any:
        pass

    @abstractmethod
    def visit_call_expression(self, node: CallExpression) -> Any:
        pass

    @abstractmethod
    def visit_assignment_expression(self, node: AssignmentExpression) -> Any:
        pass

    @abstractmethod
    def visit_array_literal(self, node: ArrayLiteral) -> Any:
        pass

    @abstractmethod
    def visit_index_expression(self, node: IndexExpression) -> Any:
        pass
