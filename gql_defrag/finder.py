"""

Find GraphQL fragments.

"""

import ast
import os
import re
from collections.abc import Container, Iterable
from pathlib import Path


def get_files(source_dir: Path, extensions: Container[str]) -> Iterable[Path]:
    """Find all pieces of GraphQL in a directory."""
    for root, _, files in os.walk(source_dir):
        for file in files:
            path = Path(root) / file
            if path.suffix in extensions:
                yield path


def extract_from_js(source_dir: Path) -> Iterable[str]:
    """Extract GraphQL from JavaScript files."""
    for path in get_files(source_dir, {".js", ".jsx", ".ts", ".tsx"}):
        contents = path.read_text()
        for doc in re.findall(r"(?:graphql|gql)`([^`]+)`", contents):
            yield doc.replace("null", '"null"')


def extract_from_standalone_files(source_dir: Path, extension: str = ".graphql"):
    """Extract GraphQL from standalone files."""
    for path in get_files(source_dir, {extension}):
        yield path.read_text()


def extract_from_relay_files(source_dir: Path) -> Iterable[str]:
    """Extract GraphQL from Relay files."""
    for path in get_files(source_dir, {".ts"}):
        if not path.name.endswith(".graphql.ts"):
            continue
        contents = path.read_text()
        for doc in re.findall(r'"text": ("(?:\\"|[^"])+")', contents):
            doc = ast.literal_eval(doc)
            yield doc.replace("null", '"null"')
