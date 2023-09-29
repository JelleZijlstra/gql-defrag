from gql_defrag import Defragmenter
from gql_defrag.finder import clean_gql

DOCUMENT = """
query SomeQuery {
    field
    name
    objectField {
        field1
    }
    ...SomeFragment
}

fragment SomeFragment on SomeType {
    fragmentField
    field
    objectField {
        field2
    }
}
"""

EXPECTED = """
query SomeQuery {
  field @gql_defrag_source(name: "SomeQuery") @gql_defrag_source(name: "SomeQuery -> SomeFragment")
  fragmentField @gql_defrag_source(name: "SomeQuery -> SomeFragment")
  name @gql_defrag_source(name: "SomeQuery")
  objectField @gql_defrag_source(name: "SomeQuery") @gql_defrag_source(name: "SomeQuery -> SomeFragment") {
    field1 @gql_defrag_source(name: "SomeQuery -> field objectField")
    field2 @gql_defrag_source(name: "SomeQuery -> SomeFragment -> field objectField")
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
