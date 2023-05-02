"""

Find GraphQL fragments.

"""

import os
from pathlib import Path
import re
from typing import Container, Iterable


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
        yield from re.findall(r"(?:graphql|gql)`([^`]+)`", contents)


def extract_from_standalone_files(source_dir: Path, extension: str = ".graphql"):
    """Extract GraphQL from standalone files."""
    for path in get_files(source_dir, {extension}):
        yield path.read_text()
