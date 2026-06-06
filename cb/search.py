"""Search helpers for snippets."""

from __future__ import annotations

from typing import List

from cb.models import Snippet


def snippet_matches(snippet: Snippet, query: str) -> bool:
    normalized_query = query.casefold()
    searchable_text = " ".join(
        [
            snippet.name,
            snippet.description,
            " ".join(snippet.tags),
            snippet.body,
        ]
    ).casefold()
    return normalized_query in searchable_text


def search_snippets(snippets: List[Snippet], query: str) -> List[Snippet]:
    return [snippet for snippet in snippets if snippet_matches(snippet, query)]
