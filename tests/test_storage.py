from pathlib import Path

import pytest

from cb.models import Snippet
from cb.storage import (
    SnippetNotFoundError,
    StorageCorruptionError,
    delete_snippet,
    find_snippet,
    init_storage,
    load_snippets,
    save_snippets,
    upsert_snippet,
)


def test_init_storage_creates_empty_json_file(tmp_path: Path) -> None:
    storage_path = tmp_path / "snippets.json"

    init_storage(storage_path)

    assert storage_path.exists()
    assert load_snippets(storage_path) == []


def test_save_and_load_snippets_round_trip(tmp_path: Path) -> None:
    storage_path = tmp_path / "snippets.json"
    snippet = Snippet(
        name="plot-hist",
        description="Histogram template",
        tags=["python", "seaborn"],
        body="import seaborn as sns",
        created_at="2026-06-02T00:00:00+00:00",
        updated_at="2026-06-02T00:00:00+00:00",
    )

    save_snippets([snippet], storage_path)

    assert load_snippets(storage_path) == [snippet]


def test_upsert_replaces_existing_snippet() -> None:
    original = Snippet(
        name="plot-hist",
        description="Old",
        tags=["python"],
        body="old body",
    )
    updated = Snippet(
        name="plot-hist",
        description="New",
        tags=["python", "seaborn"],
        body="new body",
    )

    snippets = upsert_snippet([original], updated)

    assert snippets == [updated]


def test_find_snippet_returns_matching_name() -> None:
    snippet = Snippet(name="plot-hist")

    assert find_snippet([snippet], "plot-hist") == snippet
    assert find_snippet([snippet], "missing") is None


def test_delete_snippet_removes_saved_snippet(tmp_path: Path) -> None:
    storage_path = tmp_path / "snippets.json"
    snippet = Snippet(name="plot-hist")
    save_snippets([snippet], storage_path)

    deleted = delete_snippet("plot-hist", storage_path)

    assert deleted == snippet
    assert load_snippets(storage_path) == []


def test_delete_snippet_reports_missing_name(tmp_path: Path) -> None:
    storage_path = tmp_path / "snippets.json"
    save_snippets([], storage_path)

    with pytest.raises(SnippetNotFoundError):
        delete_snippet("missing", storage_path)


def test_load_snippets_reports_corrupted_json(tmp_path: Path) -> None:
    storage_path = tmp_path / "snippets.json"
    storage_path.write_text("{not valid json", encoding="utf-8")

    with pytest.raises(StorageCorruptionError):
        load_snippets(storage_path)


def test_load_snippets_reports_missing_snippet_fields(tmp_path: Path) -> None:
    storage_path = tmp_path / "snippets.json"
    storage_path.write_text('[{"name": "plot-hist"}]', encoding="utf-8")

    with pytest.raises(StorageCorruptionError, match="missing"):
        load_snippets(storage_path)


def test_load_snippets_reports_invalid_tag_field(tmp_path: Path) -> None:
    storage_path = tmp_path / "snippets.json"
    storage_path.write_text(
        """[
          {
            "name": "plot-hist",
            "description": "Histogram template",
            "tags": "python",
            "body": "import seaborn as sns",
            "created_at": "2026-06-02T00:00:00+00:00",
            "updated_at": "2026-06-02T00:00:00+00:00"
          }
        ]""",
        encoding="utf-8",
    )

    with pytest.raises(StorageCorruptionError, match="tags"):
        load_snippets(storage_path)
