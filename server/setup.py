#!/usr/bin/env python3
"""Setup script for AetherScript."""

import os
from setuptools import setup, find_packages

# Read requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

# Read README.md for long description
with open(os.path.join(os.path.dirname(__file__), "..", "README.md"), "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="aetherscript",
    version="0.1.0",
    description="AetherScript programming language tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AetherScript Contributors",
    author_email="info@aetherscript.example.com",
    url="https://github.com/yourusername/aetherscript-vscode",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Compilers",
        "Topic :: Software Development :: Interpreters",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "aetherscript-lsp=aetherscript.lsp.server_main:main",
        ],
    },
)
