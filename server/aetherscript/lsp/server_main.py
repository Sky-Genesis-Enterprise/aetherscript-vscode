#!/usr/bin/env python3
"""Entry point for the AetherScript Language Server."""

import sys
import os
import logging
import argparse

from aetherscript.lsp.server import AetherScriptLanguageServer


def main():
    """Start the language server."""
    parser = argparse.ArgumentParser(description="AetherScript Language Server")
    parser.add_argument(
        "--log-file",
        help="Path to log file",
        default=os.path.join(os.path.dirname(__file__), "aetherscript_lsp.log")
    )
    parser.add_argument(
        "--log-level",
        help="Log level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO"
    )
    args = parser.parse_args()

    # Configure logging
    log_level = getattr(logging, args.log_level)
    logging.basicConfig(
        filename=args.log_file,
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        filemode="w"
    )

    # Start the server
    server = AetherScriptLanguageServer()
    server.start_io()


if __name__ == "__main__":
    main()
