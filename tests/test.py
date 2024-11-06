from gql_defrag import Defragmenter
from gql_defrag.finder import clean_gql

DOCUMENT = """
query SomeQuery {
    field
    name
    objectField {
        field1
        ... on SomeObject {
            field3
        }
    }
    ...SomeFragment
}

fragment SomeFragment on SomeType {
    fragmentField
    field
    objectField {
        field2
        field4: field1
    }
}
"""

EXPECTED = """
query SomeQuery {
  ... on SomeType @gql_defrag_source(name: "SomeQuery") {
    field @gql_defrag_source(name: "SomeQuery -> SomeFragment")
    fragmentField @gql_defrag_source(name: "SomeQuery -> SomeFragment")
    objectField @gql_defrag_source(name: "SomeQuery -> SomeFragment") {
      field2 @gql_defrag_source(name: "SomeQuery -> SomeFragment -> field objectField")
      field4: field1 @gql_defrag_source(name: "SomeQuery -> SomeFragment -> field objectField")
    }
  }
  field @gql_defrag_source(name: "SomeQuery")
  name @gql_defrag_source(name: "SomeQuery")
  objectField @gql_defrag_source(name: "SomeQuery") {
    ... on SomeObject @gql_defrag_source(name: "SomeQuery -> field objectField") {
      field3 @gql_defrag_source(name: "SomeQuery -> field objectField -> (inline fragment)")
    }
    field1 @gql_defrag_source(name: "SomeQuery -> field objectField")
  }
}
"""


def test_basic() -> None:
    defragmenter = Defragmenter([DOCUMENT])
    assert defragmenter.defragment("SomeQuery").strip() == EXPECTED.strip()


def test_null() -> None:
    query = 'query SomeQuery { nullableField(arg: null, arg2: "null") }'
    assert (
        clean_gql(query).strip()
        == 'query SomeQuery { nullableField(arg: "null", arg2: "null") }'
    )
