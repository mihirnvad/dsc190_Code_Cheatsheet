from cb.models import Snippet
from cb.search import search_snippets


def test_search_matches_name_description_tags_and_body() -> None:
    snippets = [
        Snippet(
            name="plot-hist",
            description="Histogram template",
            tags=["python", "seaborn"],
            body="sns.histplot(df['age'])",
        ),
        Snippet(
            name="git-reset-soft",
            description="Undo commit but keep changes staged",
            tags=["terminal", "git"],
            body="git reset --soft HEAD~1",
        ),
    ]

    assert [snippet.name for snippet in search_snippets(snippets, "seaborn")] == [
        "plot-hist"
    ]
    assert [snippet.name for snippet in search_snippets(snippets, "HEAD~1")] == [
        "git-reset-soft"
    ]


def test_search_is_case_insensitive() -> None:
    snippets = [
        Snippet(
            name="pandas-groupby",
            description="Group rows by category",
            tags=["Python", "Pandas"],
            body="df.groupby('major').size()",
        )
    ]

    assert search_snippets(snippets, "pandas") == snippets
