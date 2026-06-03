"""Local JSON storage for snippets."""

from __future__ import annotations

import json
from pathlib import Path

from cb.models import Snippet

DEFAULT_STORAGE_PATH = Path.home() / ".cb" / "snippets.json"


class StorageError(Exception):
    """Base exception for storage problems."""


class StorageCorruptionError(StorageError):
    """Raised when the snippets file cannot be parsed."""


def get_storage_path(path: Path | None = None) -> Path:
    return path or DEFAULT_STORAGE_PATH


def init_storage(path: Path | None = None) -> Path:
    storage_path = get_storage_path(path)
    storage_path.parent.mkdir(parents=True, exist_ok=True)
    if not storage_path.exists():
        storage_path.write_text("[]\n", encoding="utf-8")
    return storage_path


def load_snippets(path: Path | None = None) -> list[Snippet]:
    storage_path = get_storage_path(path)
    if not storage_path.exists():
        return []

    try:
        raw_data = json.loads(storage_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise StorageCorruptionError(f"Could not parse {storage_path}") from exc

    if not isinstance(raw_data, list):
        raise StorageCorruptionError(f"Expected a list of snippets in {storage_path}")

    snippets: list[Snippet] = []
    for item in raw_data:
        if not isinstance(item, dict):
            raise StorageCorruptionError(f"Expected snippet objects in {storage_path}")
        snippets.append(Snippet.from_dict(item))

    return snippets


def save_snippets(snippets: list[Snippet], path: Path | None = None) -> Path:
    storage_path = init_storage(path)
    data = [snippet.to_dict() for snippet in snippets]
    storage_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return storage_path
