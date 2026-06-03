from pathlib import Path

import pytest

from cb.models import Snippet
from cb.storage import StorageCorruptionError, init_storage, load_snippets, save_snippets


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


def test_load_snippets_reports_corrupted_json(tmp_path: Path) -> None:
    storage_path = tmp_path / "snippets.json"
    storage_path.write_text("{not valid json", encoding="utf-8")

    with pytest.raises(StorageCorruptionError):
        load_snippets(storage_path)
