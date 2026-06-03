from pathlib import Path

from typer.testing import CliRunner

import cb.cli
from cb.cli import app
from cb.models import Snippet
from cb.storage import load_snippets, save_snippets

runner = CliRunner()


def test_add_saves_editor_text(tmp_path: Path, monkeypatch) -> None:
    storage_path = tmp_path / "snippets.json"
    monkeypatch.setattr(cb.cli.click, "edit", lambda text, extension: "print('hi')\n")

    result = runner.invoke(
        app,
        [
            "add",
            "hello-python",
            "--tag",
            "python",
            "--description",
            "Tiny example",
        ],
        env={"CB_STORAGE_PATH": str(storage_path)},
    )

    assert result.exit_code == 0
    snippets = load_snippets(storage_path)
    assert len(snippets) == 1
    assert snippets[0].name == "hello-python"
    assert snippets[0].tags == ["python"]
    assert snippets[0].description == "Tiny example"
    assert snippets[0].body == "print('hi')\n"


def test_get_prints_snippet_metadata_and_body(tmp_path: Path) -> None:
    storage_path = tmp_path / "snippets.json"
    save_snippets(
        [
            Snippet(
                name="plot-hist",
                description="Histogram template",
                tags=["python", "seaborn"],
                body="import seaborn as sns\n",
                created_at="2026-06-02T00:00:00+00:00",
                updated_at="2026-06-02T00:00:00+00:00",
            )
        ],
        storage_path,
    )

    result = runner.invoke(
        app, ["get", "plot-hist"], env={"CB_STORAGE_PATH": str(storage_path)}
    )

    assert result.exit_code == 0
    assert "plot-hist" in result.output
    assert "Histogram template" in result.output
    assert "import seaborn as sns" in result.output


def test_list_prints_saved_snippets(tmp_path: Path) -> None:
    storage_path = tmp_path / "snippets.json"
    save_snippets([Snippet(name="git-status", tags=["git"], body="git status\n")], storage_path)

    result = runner.invoke(app, ["list"], env={"CB_STORAGE_PATH": str(storage_path)})

    assert result.exit_code == 0
    assert "git-status" in result.output
    assert "git" in result.output


def test_search_prints_matching_snippets(tmp_path: Path) -> None:
    storage_path = tmp_path / "snippets.json"
    save_snippets(
        [
            Snippet(name="plot-hist", tags=["python"], body="sns.histplot(df['age'])"),
            Snippet(name="git-status", tags=["git"], body="git status"),
        ],
        storage_path,
    )

    result = runner.invoke(app, ["search", "histplot"], env={"CB_STORAGE_PATH": str(storage_path)})

    assert result.exit_code == 0
    assert "plot-hist" in result.output
    assert "git-status" not in result.output


def test_copy_copies_snippet_body(tmp_path: Path, monkeypatch) -> None:
    storage_path = tmp_path / "snippets.json"
    save_snippets([Snippet(name="git-status", body="git status\n")], storage_path)
    copied_text = []
    monkeypatch.setattr(cb.cli, "copy_text", copied_text.append)

    result = runner.invoke(
        app, ["copy", "git-status"], env={"CB_STORAGE_PATH": str(storage_path)}
    )

    assert result.exit_code == 0
    assert copied_text == ["git status\n"]
    assert "Copied snippet to clipboard" in result.output


def test_copy_reports_clipboard_error(tmp_path: Path, monkeypatch) -> None:
    storage_path = tmp_path / "snippets.json"
    save_snippets([Snippet(name="git-status", body="git status\n")], storage_path)

    def fail_copy(text: str) -> None:
        raise cb.cli.ClipboardError("Clipboard unavailable")

    monkeypatch.setattr(cb.cli, "copy_text", fail_copy)

    result = runner.invoke(
        app, ["copy", "git-status"], env={"CB_STORAGE_PATH": str(storage_path)}
    )

    assert result.exit_code == 1
    assert "Clipboard unavailable" in result.output


def test_delete_removes_snippet_after_confirmation(tmp_path: Path) -> None:
    storage_path = tmp_path / "snippets.json"
    save_snippets([Snippet(name="plot-hist")], storage_path)

    result = runner.invoke(
        app,
        ["delete", "plot-hist"],
        input="y\n",
        env={"CB_STORAGE_PATH": str(storage_path)},
    )

    assert result.exit_code == 0
    assert load_snippets(storage_path) == []


def test_missing_snippet_exits_with_error(tmp_path: Path) -> None:
    storage_path = tmp_path / "snippets.json"
    save_snippets([], storage_path)

    result = runner.invoke(
        app, ["get", "missing"], env={"CB_STORAGE_PATH": str(storage_path)}
    )

    assert result.exit_code == 1
    assert "No snippet named 'missing'" in result.output
