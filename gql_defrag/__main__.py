import argparse
import os
from pathlib import Path

from .defrag import Defragmenter
from .finder import (
    extract_from_js,
    extract_from_relay_files,
    extract_from_standalone_files,
)


def main():
    parser = argparse.ArgumentParser(description="Defragment GraphQL queries")
    parser.add_argument(
        "--js-dir",
        help="Directory with JavaScript files containing GraphQL fragments and queries",
    )
    parser.add_argument(
        "--graphql-dir", help="Directory with GraphQL files with .graphql extensions"
    )
    parser.add_argument(
        "--relay-dir", help="Directory with Relay files with .graphql.ts extensions"
    )
    parser.add_argument(
        "--output-dir", help="Directory to write defragmented queries to"
    )
    parser.add_argument(
        "--include-source",
        help="Include verbose source information",
        action="store_true",
        default=False,
    )
    args = parser.parse_args()

    defragmenter = Defragmenter()
    if args.js_dir:
        for doc in extract_from_js(Path(args.js_dir)):
            defragmenter.add_document(doc)
    if args.graphql_dir:
        for doc in extract_from_standalone_files(Path(args.graphql_dir)):
            defragmenter.add_document(doc)
    if args.relay_dir:
        for doc in extract_from_relay_files(Path(args.relay_dir)):
            defragmenter.add_document(doc)
    if args.output_dir:
        output_dir = Path(args.output_dir)
        os.makedirs(output_dir, exist_ok=True)
        for query_name, query in defragmenter.defragment_all(
            add_source=args.include_source
        ):
            with (output_dir / f"{query_name}.graphql").open("w") as f:
                f.write(query)


if __name__ == "__main__":
    main()
