"""Local JSON storage for snippets."""

from __future__ import annotations

import json
import os
from pathlib import Path

from cb.models import Snippet

DEFAULT_STORAGE_PATH = Path.home() / ".cb" / "snippets.json"
STORAGE_PATH_ENV_VAR = "CB_STORAGE_PATH"


class StorageError(Exception):
    """Base exception for storage problems."""


class StorageCorruptionError(StorageError):
    """Raised when the snippets file cannot be parsed."""


class SnippetNotFoundError(StorageError):
    """Raised when a requested snippet does not exist."""


def get_storage_path(path: Path | None = None) -> Path:
    if path is not None:
        return path

    configured_path = os.environ.get(STORAGE_PATH_ENV_VAR)
    if configured_path:
        return Path(configured_path).expanduser()

    return DEFAULT_STORAGE_PATH


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


def find_snippet(snippets: list[Snippet], name: str) -> Snippet | None:
    for snippet in snippets:
        if snippet.name == name:
            return snippet
    return None


def get_snippet(name: str, path: Path | None = None) -> Snippet:
    snippet = find_snippet(load_snippets(path), name)
    if snippet is None:
        raise SnippetNotFoundError(f"No snippet named '{name}'")
    return snippet


def upsert_snippet(snippets: list[Snippet], snippet: Snippet) -> list[Snippet]:
    updated_snippets = list(snippets)
    for index, existing in enumerate(updated_snippets):
        if existing.name == snippet.name:
            updated_snippets[index] = snippet
            return updated_snippets

    updated_snippets.append(snippet)
    return updated_snippets


def delete_snippet(name: str, path: Path | None = None) -> Snippet:
    snippets = load_snippets(path)
    snippet = find_snippet(snippets, name)
    if snippet is None:
        raise SnippetNotFoundError(f"No snippet named '{name}'")

    save_snippets([item for item in snippets if item.name != name], path)
    return snippet
