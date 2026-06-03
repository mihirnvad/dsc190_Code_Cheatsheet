from pathlib import Path

from typer.testing import CliRunner

import cb.cli
from cb.cli import app
from cb.models import Snippet
from cb.storage import load_snippets, save_snippets

runner = CliRunner()


def test_version_option_prints_installed_version() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.output.strip().startswith("cb ")


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


def test_add_overwrites_body_and_preserves_metadata_when_flags_are_omitted(
    tmp_path: Path, monkeypatch
) -> None:
    storage_path = tmp_path / "snippets.json"
    existing = Snippet(
        name="plot-hist",
        description="Histogram template",
        tags=["python", "seaborn"],
        body="old body\n",
        created_at="2026-06-02T00:00:00+00:00",
        updated_at="2026-06-02T00:00:00+00:00",
    )
    save_snippets([existing], storage_path)
    monkeypatch.setattr(cb.cli.click, "edit", lambda text, extension: "new body\n")
    monkeypatch.setattr(cb.cli, "utc_now_iso", lambda: "2026-06-03T00:00:00+00:00")

    result = runner.invoke(
        app,
        ["add", "plot-hist"],
        input="y\n",
        env={"CB_STORAGE_PATH": str(storage_path)},
    )

    assert result.exit_code == 0
    [snippet] = load_snippets(storage_path)
    assert snippet.description == existing.description
    assert snippet.tags == existing.tags
    assert snippet.body == "new body\n"
    assert snippet.created_at == existing.created_at
    assert snippet.updated_at == "2026-06-03T00:00:00+00:00"


def test_add_replaces_metadata_when_overwrite_flags_are_supplied(
    tmp_path: Path, monkeypatch
) -> None:
    storage_path = tmp_path / "snippets.json"
    save_snippets(
        [
            Snippet(
                name="plot-hist",
                description="Old description",
                tags=["old"],
                body="old body\n",
            )
        ],
        storage_path,
    )
    monkeypatch.setattr(cb.cli.click, "edit", lambda text, extension: "new body\n")

    result = runner.invoke(
        app,
        [
            "add",
            "plot-hist",
            "--description",
            "New description",
            "--tag",
            "python",
        ],
        input="y\n",
        env={"CB_STORAGE_PATH": str(storage_path)},
    )

    assert result.exit_code == 0
    [snippet] = load_snippets(storage_path)
    assert snippet.description == "New description"
    assert snippet.tags == ["python"]


def test_add_cancelled_overwrite_leaves_existing_snippet(
    tmp_path: Path, monkeypatch
) -> None:
    storage_path = tmp_path / "snippets.json"
    existing = Snippet(name="plot-hist", body="old body\n")
    save_snippets([existing], storage_path)

    def fail_edit(text: str, extension: str) -> str:
        raise AssertionError("Editor should not open after cancelling overwrite")

    monkeypatch.setattr(cb.cli.click, "edit", fail_edit)

    result = runner.invoke(
        app,
        ["add", "plot-hist"],
        input="n\n",
        env={"CB_STORAGE_PATH": str(storage_path)},
    )

    assert result.exit_code == 0
    assert "Cancelled" in result.output
    assert load_snippets(storage_path) == [existing]


def test_add_empty_editor_text_does_not_save(tmp_path: Path, monkeypatch) -> None:
    storage_path = tmp_path / "snippets.json"
    monkeypatch.setattr(cb.cli.click, "edit", lambda text, extension: "\n\n")

    result = runner.invoke(
        app, ["add", "empty"], env={"CB_STORAGE_PATH": str(storage_path)}
    )

    assert result.exit_code == 0
    assert "Nothing saved" in result.output
    assert load_snippets(storage_path) == []


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


def test_delete_cancelled_keeps_snippet(tmp_path: Path) -> None:
    storage_path = tmp_path / "snippets.json"
    snippet = Snippet(name="plot-hist")
    save_snippets([snippet], storage_path)

    result = runner.invoke(
        app,
        ["delete", "plot-hist"],
        input="n\n",
        env={"CB_STORAGE_PATH": str(storage_path)},
    )

    assert result.exit_code == 0
    assert "Cancelled" in result.output
    assert load_snippets(storage_path) == [snippet]


def test_missing_snippet_exits_with_error(tmp_path: Path) -> None:
    storage_path = tmp_path / "snippets.json"
    save_snippets([], storage_path)

    result = runner.invoke(
        app, ["get", "missing"], env={"CB_STORAGE_PATH": str(storage_path)}
    )

    assert result.exit_code == 1
    assert "No snippet named 'missing'" in result.output
