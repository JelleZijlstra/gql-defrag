from collections.abc import Iterable, Sequence
from copy import deepcopy
from typing import Optional

import graphql
from graphql.language import ast
from graphql.language.printer import print_ast
from graphql.language.source import Source


class Defragmenter:
    query_to_defn: dict[str, ast.OperationDefinition]
    fragment_to_defn: dict[str, ast.FragmentDefinition]

    def __init__(self, documents: Sequence[str] = ()) -> None:
        self.query_to_defn = {}
        self.fragment_to_defn = {}
        for document in documents:
            self.add_document(document)

    def add_document(self, document: str) -> None:
        source = Source(document)
        doc = graphql.parse(source)
        assert isinstance(doc, ast.Document)
        for defn in doc.definitions:
            if isinstance(defn, ast.FragmentDefinition):
                self.fragment_to_defn[defn.name.value] = defn
            elif isinstance(defn, ast.OperationDefinition):
                self.query_to_defn[defn.name.value] = defn
            else:
                raise ValueError(f"Unknown definition type: {defn!r}")

    def defragment(self, query_name: str, *, add_source: bool = True) -> str:
        query = self.query_to_defn[query_name]
        new_query = ast.OperationDefinition(
            operation=query.operation,
            name=query.name,
            variable_definitions=query.variable_definitions,
            directives=query.directives,
            selection_set=self._defragment_selection_set(
                query.selection_set, source=query_name if add_source else None
            ),
            loc=query.loc,
        )
        new_doc = ast.Document(definitions=[new_query])
        return print_ast(new_doc)

    def defragment_all(self, add_source: bool = True) -> Iterable[tuple[str, str]]:
        for query_name in self.query_to_defn:
            yield query_name, self.defragment(query_name, add_source=add_source)

    def _defragment_selection_set(
        self, selection_set: ast.SelectionSet, source: Optional[str]
    ) -> ast.SelectionSet:
        new_selections, final_list = self._parse_selection_set(
            selection_set.selections, source
        )
        for _, nodes in sorted(new_selections.items()):
            new_node = deepcopy(nodes[0])
            for node in nodes[1:]:
                new_node.directives.extend(node.directives)
            final_list.append(new_node)
        return ast.SelectionSet(selections=final_list, loc=selection_set.loc)

    def _parse_selection_set(
        self, selections: Sequence[ast.Node], source: Optional[str]
    ) -> tuple[dict[str, list[ast.Node]], list[ast.Node]]:
        new_selections: dict[str, list[ast.Node]] = {}
        final_list: list[ast.Node] = []
        for selection in selections:
            if isinstance(selection, ast.Field):
                name = (
                    selection.alias.value if selection.alias else selection.name.value
                )
                new_field = ast.Field(
                    name=selection.name,
                    alias=selection.alias,
                    arguments=selection.arguments,
                    directives=_add_source(selection.directives, source),
                    selection_set=self._defragment_selection_set(
                        selection.selection_set,
                        f"field {name}" if source is not None else None,
                    )
                    if selection.selection_set
                    else None,
                    loc=selection.loc,
                )
                new_selections.setdefault(name, []).append(new_field)
            elif isinstance(selection, ast.FragmentSpread):
                # We ignore any directives here
                fragment_def = self.fragment_to_defn[selection.name.value]
                frag_sels, frag_list = self._parse_selection_set(
                    fragment_def.selection_set.selections,
                    f"{source} -> {selection.name.value}"
                    if source is not None
                    else None,
                )
                for name, nodes in frag_sels.items():
                    new_selections.setdefault(name, []).extend(nodes)
                final_list += frag_list
            elif isinstance(selection, ast.InlineFragment):
                new_frag = ast.InlineFragment(
                    type_condition=selection.type_condition,
                    directives=_add_source(selection.directives, source),
                    selection_set=self._defragment_selection_set(
                        selection.selection_set,
                        f"{source} -> (inline fragment)"
                        if source is not None
                        else None,
                    ),
                )
                final_list.append(new_frag)
            else:
                raise ValueError(f"Unknown selection type: {selection!r}")
        return new_selections, final_list


def _add_source(
    directives: Optional[list[ast.Directive]], source: Optional[str]
) -> Optional[list[ast.Directive]]:
    if source is None:
        return directives
    if not directives:
        return [_make_defrag_directive(source)]
    new_directives: list[ast.Directive] = []
    found_existing = False
    for directive in directives:
        if directive.name.value == "gql_defrag_source":
            found_existing = True
            new_directives.append(
                _make_defrag_directive(source, directive.arguments[0].value.value)
            )
        else:
            new_directives.append(directive)
    if not found_existing:
        new_directives.append(_make_defrag_directive(source))
    return new_directives


def _make_defrag_directive(
    source: str, existing_source: Optional[str] = None
) -> ast.Directive:
    if existing_source is None:
        final_source = source
    else:
        final_source = f"{source} -> {existing_source}"
    return ast.Directive(
        name=ast.Name(value="gql_defrag_source"),
        arguments=[
            ast.Argument(
                name=ast.Name(value="name"), value=ast.StringValue(value=final_source)
            )
        ],
    )
