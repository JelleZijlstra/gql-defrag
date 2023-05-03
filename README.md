# gql-defrag

Do you have complex GraphQL queries that are made up of lot of fragments? Do you want to
figure out who is querying all those fields? Then gql-defrag can help you. It takes in
the text of all your queries and fragments, and returns a new query that inlines all the
fragments and labels fields with their origin.

Example:

    >>> from gql_defrag import Defragmenter
    >>> defrag = Defragmenter(["""
    ... query SomeQuery {
    ...     field
    ...     name
    ...     ...SomeFragment
    ... }
    ...
    ... fragment SomeFragment on SomeType {
    ...     fragmentField
    ...     field
    ... }
    ... """])
    >>> print(defrag.defragment("SomeQuery"))
    query SomeQuery {
      field @gql_defrag_source(name: "SomeQuery") @gql_defrag_source(name: "SomeQuery -> SomeFragment")
      fragmentField @gql_defrag_source(name: "SomeQuery -> SomeFragment")
      name @gql_defrag_source(name: "SomeQuery")
    }

## Programmatic usage

### `gql_defrag.Defragmenter(documents: Sequence[str])`

Instantiate a `Defragmenter` to start defragmenting some queries. Pass in a series of
GraphQL documents. Each may contain one or more queries, fragments, or both.

#### `Defragmenter.add_document(document: str) -> None`

Add a document to the `Defragmenter`. The document may contain any number of queries or
fragments.

#### `Defragmenter.defragment(query_name: str, *, add_source: bool = True) -> str`

Return a defragmented version of the operation (query, mutation, or subscription) named
`query_name`. If `add_source` is True, add `@gql_defrag_source` directives explaining
what sequence of fragments triggered each field.

#### `Defragmenter.defragment_all(*, add_source: bool = True) -> Iterable[tuple[str, str]]`

Yields pairs of (query name, defragmented query) for all operations that the
`Defragmenter` knows about.

## Command-line usage

```
$ python -m gql_defrag --help
usage: __main__.py [-h] [--js-dir JS_DIR] [--graphql-dir GRAPHQL_DIR] [--relay-dir RELAY_DIR] [--output-dir OUTPUT_DIR] [--include-source]

Defrag GraphQL queries

options:
  -h, --help            show this help message and exit
  --js-dir JS_DIR       Directory with JavaScript files containing GraphQL fragments and queries
  --graphql-dir GRAPHQL_DIR
                        Directory with GraphQL files with .graphql extensions
  --relay-dir RELAY_DIR
                        Directory with Relay files with .graphql.ts extensions
  --output-dir OUTPUT_DIR
                        Directory to write defragmented queries to
  --include-source      Include verbose source information
```

The command-line interface collects GraphQL queries from one or more directories and
outputs defragmented queries to an output directory.

There are three ways to find GraphQL queries:

- `--graphql-dir` looks at a directory containing `.graphql` files that contain GraphQL
  queries
- `--js-dir` looks at a directory containing JavaScript or TypeScript files that contain
  pieces of GraphQL within template literals prefixed with `graphql` or `gql`. The code
  looks at files with the extensions `.js`, `.jsx`, `.ts`, and `.tsx`.
- `--relay-dir` looks at a directory containing Relay generated files with the
  `.graphql.ts` extension.

Defragmented files are placed in the directory specified by `--output-dir`. If the
directory does not exist, it is created. The file names are of the form
`<query name>.graphql`.

If `--include-source` is given, `@gql_defrag_source` are added with precise source
information for each field.

## Changelog

### Version 0.1.0 (May 3, 2023)

Initial public release.
