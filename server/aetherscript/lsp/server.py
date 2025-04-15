"""Language Server Protocol implementation for AetherScript."""

import os
import logging
from typing import List, Dict, Optional, Any, Union
import json

from pygls.server import LanguageServer
from pygls.lsp.types import (
    CompletionItem, CompletionItemKind, CompletionList, CompletionOptions, CompletionParams,
    Diagnostic, DiagnosticSeverity, DidChangeTextDocumentParams, DidOpenTextDocumentParams,
    DidSaveTextDocumentParams, DocumentFormattingParams, DocumentSymbol, DocumentSymbolParams,
    Hover, HoverParams, InitializeParams, InitializeResult, Location, MarkupContent, MarkupKind,
    Position, Range, ReferenceParams, SymbolInformation, SymbolKind, TextDocumentPositionParams,
    TextEdit, WorkspaceEdit, WorkspaceSymbolParams
)

from aetherscript.parser.lexer import Lexer, Token, TokenType
from aetherscript.parser.parser import Parser
from aetherscript.analyzer.type_checker import TypeChecker, TypeError
from aetherscript.analyzer.semantic_analyzer import SemanticAnalyzer, Definition, Reference, Location as AetherLocation


# Set up logging
logging.basicConfig(filename="aetherscript_lsp.log", level=logging.DEBUG, filemode="w")
logger = logging.getLogger("aetherscript_lsp")


class AetherScriptLanguageServer(LanguageServer):
    """Language Server Protocol implementation for AetherScript."""

    def __init__(self):
        """Initialize the language server."""
        super().__init__("aetherscript-ls", "v0.1.0")

        # Document cache
        self.document_cache: Dict[str, str] = {}

        # Analyzers
        self.parsers: Dict[str, Parser] = {}
        self.type_checkers: Dict[str, TypeChecker] = {}
        self.semantic_analyzers: Dict[str, SemanticAnalyzer] = {}

        # Register LSP methods
        self._register_methods()

    def _register_methods(self):
        """Register LSP methods."""
        self.feature(
            self.lsp.methods.TEXT_DOCUMENT_DID_OPEN,
            self.on_did_open
        )
        self.feature(
            self.lsp.methods.TEXT_DOCUMENT_DID_CHANGE,
            self.on_did_change
        )
        self.feature(
            self.lsp.methods.TEXT_DOCUMENT_DID_SAVE,
            self.on_did_save
        )
        self.feature(
            self.lsp.methods.TEXT_DOCUMENT_COMPLETION,
            self.on_completion
        )
        self.feature(
            self.lsp.methods.TEXT_DOCUMENT_HOVER,
            self.on_hover
        )
        self.feature(
            self.lsp.methods.TEXT_DOCUMENT_DEFINITION,
            self.on_definition
        )
        self.feature(
            self.lsp.methods.TEXT_DOCUMENT_REFERENCES,
            self.on_references
        )
        self.feature(
            self.lsp.methods.TEXT_DOCUMENT_DOCUMENT_SYMBOL,
            self.on_document_symbol
        )
        self.feature(
            self.lsp.methods.WORKSPACE_SYMBOL,
            self.on_workspace_symbol
        )

    def on_initialize(self, params: InitializeParams) -> InitializeResult:
        """Initialize the language server."""
        logger.info("Initializing AetherScript Language Server")

        # Initialize result
        result = InitializeResult(
            capabilities={
                "textDocumentSync": {
                    "openClose": True,
                    "change": 1,  # Full content sync
                    "save": {"includeText": True}
                },
                "completionProvider": {
                    "triggerCharacters": ["."]
                },
                "hoverProvider": True,
                "definitionProvider": True,
                "referencesProvider": True,
                "documentSymbolProvider": True,
                "workspaceSymbolProvider": True
            }
        )

        return result

    async def on_did_open(self, params: DidOpenTextDocumentParams) -> None:
        """Handle text document open event."""
        uri = params.text_document.uri
        text = params.text_document.text

        logger.info(f"Document opened: {uri}")

        # Cache the document
        self.document_cache[uri] = text

        # Analyze the document
        await self._analyze_document(uri, text)

    async def on_did_change(self, params: DidChangeTextDocumentParams) -> None:
        """Handle text document change event."""
        uri = params.text_document.uri

        # Get the full content change
        if len(params.content_changes) > 0:
            text = params.content_changes[0].text
            self.document_cache[uri] = text

            # Analyze the document
            await self._analyze_document(uri, text)

    async def on_did_save(self, params: DidSaveTextDocumentParams) -> None:
        """Handle text document save event."""
        uri = params.text_document.uri

        if uri in self.document_cache:
            text = self.document_cache[uri]

            # Analyze the document
            await self._analyze_document(uri, text)

    async def on_completion(self, params: CompletionParams) -> CompletionList:
        """Handle completion request."""
        uri = params.text_document.uri
        position = params.position

        if uri not in self.document_cache:
            return CompletionList(is_incomplete=False, items=[])

        # Get semantic analyzer
        semantic_analyzer = self.semantic_analyzers.get(uri)
        if not semantic_analyzer:
            return CompletionList(is_incomplete=False, items=[])

        # Get current word
        line = position.line
        character = position.character
        text = self.document_cache[uri]
        lines = text.split("\n")
        current_line = lines[line] if line < len(lines) else ""

        # Find current word
        word_start = character
        while word_start > 0 and (current_line[word_start - 1].isalnum() or current_line[word_start - 1] == "_"):
            word_start -= 1

        current_word = current_line[word_start:character]

        # Find completions
        completions = []

        # Add symbols from the current scope
        for name, definitions in semantic_analyzer.definitions.items():
            for definition in definitions:
                if current_word and not name.startswith(current_word):
                    continue

                kind = None
                if definition.kind == "function":
                    kind = CompletionItemKind.Function
                elif definition.kind == "variable":
                    kind = CompletionItemKind.Variable
                elif definition.kind == "parameter":
                    kind = CompletionItemKind.Variable
                else:
                    kind = CompletionItemKind.Text

                completions.append(
                    CompletionItem(
                        label=name,
                        kind=kind,
                        detail=f"{definition.kind}: {definition.type_name}",
                        documentation=definition.detail,
                        insert_text=name
                    )
                )

        # Add keywords
        keywords = [
            "if", "else", "elif", "while", "for", "return", "break", "continue",
            "function", "spell", "ritual", "conjure", "entity", "realm", "dimension"
        ]

        for keyword in keywords:
            if current_word and not keyword.startswith(current_word):
                continue

            completions.append(
                CompletionItem(
                    label=keyword,
                    kind=CompletionItemKind.Keyword,
                    detail="keyword",
                    insert_text=keyword
                )
            )

        return CompletionList(is_incomplete=False, items=completions)

    async def on_hover(self, params: HoverParams) -> Optional[Hover]:
        """Handle hover request."""
        uri = params.text_document.uri
        position = params.position

        if uri not in self.document_cache:
            return None

        # Get semantic analyzer
        semantic_analyzer = self.semantic_analyzers.get(uri)
        if not semantic_analyzer:
            return None

        # Get word at position
        line = position.line
        character = position.character
        text = self.document_cache[uri]
        lines = text.split("\n")
        current_line = lines[line] if line < len(lines) else ""

        # Find word at position
        word_start = character
        while word_start > 0 and (current_line[word_start - 1].isalnum() or current_line[word_start - 1] == "_"):
            word_start -= 1

        word_end = character
        while word_end < len(current_line) and (current_line[word_end].isalnum() or current_line[word_end] == "_"):
            word_end += 1

        word = current_line[word_start:word_end]

        if not word:
            return None

        # Find hover info
        lsp_location = AetherLocation(line + 1, character + 1)
        hover_info = semantic_analyzer.find_hover_info(word, lsp_location)

        if hover_info:
            return Hover(
                contents=MarkupContent(
                    kind=MarkupKind.Markdown,
                    value=f"```aetherscript\n{hover_info}\n```"
                ),
                range=Range(
                    start=Position(line=line, character=word_start),
                    end=Position(line=line, character=word_end)
                )
            )

        return None

    async def on_definition(self, params: TextDocumentPositionParams) -> Optional[Location]:
        """Handle go to definition request."""
        uri = params.text_document.uri
        position = params.position

        if uri not in self.document_cache:
            return None

        # Get semantic analyzer
        semantic_analyzer = self.semantic_analyzers.get(uri)
        if not semantic_analyzer:
            return None

        # Get word at position
        line = position.line
        character = position.character
        text = self.document_cache[uri]
        lines = text.split("\n")
        current_line = lines[line] if line < len(lines) else ""

        # Find word at position
        word_start = character
        while word_start > 0 and (current_line[word_start - 1].isalnum() or current_line[word_start - 1] == "_"):
            word_start -= 1

        word_end = character
        while word_end < len(current_line) and (current_line[word_end].isalnum() or current_line[word_end] == "_"):
            word_end += 1

        word = current_line[word_start:word_end]

        if not word:
            return None

        # Find definition
        lsp_location = AetherLocation(line + 1, character + 1)
        definition = semantic_analyzer.find_definition(word, lsp_location)

        if definition:
            return Location(
                uri=uri,
                range=Range(
                    start=Position(line=definition.location.line - 1, character=definition.location.column - 1),
                    end=Position(line=definition.location.line - 1, character=definition.location.column - 1 + len(word))
                )
            )

        return None

    async def on_references(self, params: ReferenceParams) -> List[Location]:
        """Handle find references request."""
        uri = params.text_document.uri
        position = params.position

        if uri not in self.document_cache:
            return []

        # Get semantic analyzer
        semantic_analyzer = self.semantic_analyzers.get(uri)
        if not semantic_analyzer:
            return []

        # Get word at position
        line = position.line
        character = position.character
        text = self.document_cache[uri]
        lines = text.split("\n")
        current_line = lines[line] if line < len(lines) else ""

        # Find word at position
        word_start = character
        while word_start > 0 and (current_line[word_start - 1].isalnum() or current_line[word_start - 1] == "_"):
            word_start -= 1

        word_end = character
        while word_end < len(current_line) and (current_line[word_end].isalnum() or current_line[word_end] == "_"):
            word_end += 1

        word = current_line[word_start:word_end]

        if not word:
            return []

        # Find definition
        lsp_location = AetherLocation(line + 1, character + 1)
        definition = semantic_analyzer.find_definition(word, lsp_location)

        if not definition:
            return []

        # Find references
        references = semantic_analyzer.find_all_references(word, definition.location)

        # Convert to LSP locations
        lsp_references = []
        for reference in references:
            lsp_references.append(
                Location(
                    uri=uri,
                    range=Range(
                        start=Position(line=reference.location.line - 1, character=reference.location.column - 1),
                        end=Position(line=reference.location.line - 1, character=reference.location.column - 1 + len(word))
                    )
                )
            )

        return lsp_references

    async def on_document_symbol(self, params: DocumentSymbolParams) -> List[DocumentSymbol]:
        """Handle document symbol request."""
        uri = params.text_document.uri

        if uri not in self.document_cache:
            return []

        # Get semantic analyzer
        semantic_analyzer = self.semantic_analyzers.get(uri)
        if not semantic_analyzer:
            return []

        # Find symbols
        symbols = []
        for name, definitions in semantic_analyzer.definitions.items():
            for definition in definitions:
                kind = None
                if definition.kind == "function":
                    kind = SymbolKind.Function
                elif definition.kind == "variable":
                    kind = SymbolKind.Variable
                elif definition.kind == "parameter":
                    kind = SymbolKind.Variable
                else:
                    kind = SymbolKind.String

                symbols.append(
                    SymbolInformation(
                        name=name,
                        kind=kind,
                        location=Location(
                            uri=uri,
                            range=Range(
                                start=Position(line=definition.location.line - 1, character=definition.location.column - 1),
                                end=Position(line=definition.location.line - 1, character=definition.location.column - 1 + len(name))
                            )
                        ),
                        container_name=definition.kind
                    )
                )

        return symbols

    async def on_workspace_symbol(self, params: WorkspaceSymbolParams) -> List[SymbolInformation]:
        """Handle workspace symbol request."""
        query = params.query.lower()

        # Find symbols in all documents
        symbols = []
        for uri, semantic_analyzer in self.semantic_analyzers.items():
            for name, definitions in semantic_analyzer.definitions.items():
                if query and query not in name.lower():
                    continue

                for definition in definitions:
                    kind = None
                    if definition.kind == "function":
                        kind = SymbolKind.Function
                    elif definition.kind == "variable":
                        kind = SymbolKind.Variable
                    elif definition.kind == "parameter":
                        kind = SymbolKind.Variable
                    else:
                        kind = SymbolKind.String

                    symbols.append(
                        SymbolInformation(
                            name=name,
                            kind=kind,
                            location=Location(
                                uri=uri,
                                range=Range(
                                    start=Position(line=definition.location.line - 1, character=definition.location.column - 1),
                                    end=Position(line=definition.location.line - 1, character=definition.location.column - 1 + len(name))
                                )
                            ),
                            container_name=definition.kind
                        )
                    )

        return symbols

    async def _analyze_document(self, uri: str, text: str) -> None:
        """Analyze a document and publish diagnostics."""
        logger.info(f"Analyzing document: {uri}")

        # Parse the document
        parser = Parser(text)
        ast = parser.parse()
        self.parsers[uri] = parser

        # Collect parse errors
        parse_errors = parser.errors

        # Type check the document
        type_checker = TypeChecker()
        type_errors = type_checker.check(ast)
        self.type_checkers[uri] = type_checker

        # Semantic analysis
        semantic_analyzer = SemanticAnalyzer()
        semantic_info = semantic_analyzer.analyze(ast)
        self.semantic_analyzers[uri] = semantic_analyzer

        # Collect semantic errors
        semantic_errors = semantic_info.errors

        # Convert errors to diagnostics
        diagnostics = []

        # Add parse errors
        for error in parse_errors:
            diagnostics.append(
                Diagnostic(
                    range=Range(
                        start=Position(line=error.token.line - 1, character=error.token.column - 1),
                        end=Position(line=error.token.line - 1, character=error.token.column - 1 + len(error.token.value))
                    ),
                    message=error.message,
                    severity=DiagnosticSeverity.Error,
                    source="aetherscript-parser"
                )
            )

        # Add type errors
        for error in type_errors:
            diagnostics.append(
                Diagnostic(
                    range=Range(
                        start=Position(line=error.line - 1, character=error.column - 1),
                        end=Position(line=error.line - 1, character=error.column)
                    ),
                    message=error.message,
                    severity=DiagnosticSeverity.Error,
                    source="aetherscript-type-checker"
                )
            )

        # Add semantic errors
        for error in semantic_errors:
            # Parse the error message to extract line and column information
            parts = error.split(" at ")
            if len(parts) >= 2:
                location_parts = parts[-1].split(":")
                if len(location_parts) >= 2:
                    try:
                        line = int(location_parts[0])
                        column = int(location_parts[1])

                        diagnostics.append(
                            Diagnostic(
                                range=Range(
                                    start=Position(line=line - 1, character=column - 1),
                                    end=Position(line=line - 1, character=column)
                                ),
                                message=parts[0],
                                severity=DiagnosticSeverity.Warning,
                                source="aetherscript-semantic-analyzer"
                            )
                        )
                    except ValueError:
                        # Fallback to a generic location
                        diagnostics.append(
                            Diagnostic(
                                range=Range(
                                    start=Position(line=0, character=0),
                                    end=Position(line=0, character=1)
                                ),
                                message=error,
                                severity=DiagnosticSeverity.Warning,
                                source="aetherscript-semantic-analyzer"
                            )
                        )
            else:
                # Fallback to a generic location
                diagnostics.append(
                    Diagnostic(
                        range=Range(
                            start=Position(line=0, character=0),
                            end=Position(line=0, character=1)
                        ),
                        message=error,
                        severity=DiagnosticSeverity.Warning,
                        source="aetherscript-semantic-analyzer"
                    )
                )

        # Publish diagnostics
        self.publish_diagnostics(uri, diagnostics)
