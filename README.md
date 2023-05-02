# gql-defrag

Do you have complex GraphQL queries that are made up of lot of fragments? Do you want to figure out who is querying all those fields? Then gql-defrag can help you. It takes in the text of all your queries and fragments, and returns a new query that inlines all the fragments and labels fields with their origin.

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
