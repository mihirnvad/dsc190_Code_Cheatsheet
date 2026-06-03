"""Typer CLI entry point for Code Boilerplate Vault."""

from __future__ import annotations

from typing import Annotated

import click
import typer
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

from cb.clipboard import ClipboardError, copy_text
from cb.models import Snippet, utc_now_iso
from cb.search import search_snippets
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

app = typer.Typer(
    help="Code Boilerplate Vault: save, find, and reuse code snippets from the terminal."
)
console = Console()
error_console = Console(stderr=True)


def _exit_with_error(message: str) -> None:
    error_console.print(f"[red]Error:[/red] {message}")
    raise typer.Exit(code=1)


def _load_snippets_or_exit() -> list[Snippet]:
    try:
        return load_snippets()
    except StorageCorruptionError as exc:
        _exit_with_error(str(exc))


def _save_snippets_or_exit(snippets: list[Snippet]) -> None:
    try:
        save_snippets(snippets)
    except StorageCorruptionError as exc:
        _exit_with_error(str(exc))


def _normalize_tags(tags: list[str] | None) -> list[str]:
    normalized_tags: list[str] = []
    for tag in tags or []:
        normalized_tag = tag.strip()
        if normalized_tag and normalized_tag not in normalized_tags:
            normalized_tags.append(normalized_tag)
    return normalized_tags


def _guess_lexer(snippet: Snippet) -> str:
    tags = {tag.casefold() for tag in snippet.tags}
    body_start = snippet.body.strip().splitlines()[0] if snippet.body.strip() else ""

    if {"python", "py", "pandas", "seaborn"} & tags:
        return "python"
    if {"shell", "bash", "terminal", "cli", "command", "git"} & tags:
        return "bash"
    if body_start.startswith(("git ", "uv ", "pip ", "python ", "pytest ", "cd ")):
        return "bash"
    if "import " in snippet.body or "def " in snippet.body:
        return "python"
    return "text"


def _print_snippet_table(snippets: list[Snippet], title: str) -> None:
    table = Table(title=title)
    table.add_column("name", style="bold cyan")
    table.add_column("description")
    table.add_column("tags")
    table.add_column("created_at")
    table.add_column("updated_at")

    for snippet in snippets:
        table.add_row(
            snippet.name,
            snippet.description or "-",
            ", ".join(snippet.tags) or "-",
            snippet.created_at,
            snippet.updated_at,
        )

    console.print(table)


@app.command()
def init() -> None:
    """Create the local snippets storage file."""
    storage_path = init_storage()
    console.print(f"[green]Storage ready:[/green] {storage_path}")


@app.command()
def add(
    name: Annotated[str, typer.Argument(help="Name to save the snippet under.")],
    tag: Annotated[
        list[str] | None,
        typer.Option("--tag", "-t", help="Tag for the snippet. Can be used multiple times."),
    ] = None,
    description: Annotated[
        str,
        typer.Option("--description", "-d", help="Short description of the snippet."),
    ] = "",
) -> None:
    """Open an editor and save a snippet."""
    snippets = _load_snippets_or_exit()
    existing = find_snippet(snippets, name)

    if existing is not None:
        should_overwrite = typer.confirm(
            f"Snippet '{name}' already exists. Overwrite?", default=False
        )
        if not should_overwrite:
            console.print("[yellow]Cancelled.[/yellow]")
            return

    initial_text = existing.body if existing is not None else ""
    edited_text = click.edit(text=initial_text, extension=".py")

    if edited_text is None or not edited_text.strip():
        console.print("[yellow]No snippet text entered. Nothing saved.[/yellow]")
        return

    now = utc_now_iso()
    snippet = Snippet(
        name=name,
        description=description.strip(),
        tags=_normalize_tags(tag),
        body=edited_text.rstrip() + "\n",
        created_at=existing.created_at if existing is not None else now,
        updated_at=now,
    )
    _save_snippets_or_exit(upsert_snippet(snippets, snippet))
    console.print(f"[green]Saved snippet:[/green] {name}")


@app.command()
def get(name: Annotated[str, typer.Argument(help="Snippet name to print.")]) -> None:
    """Print a saved snippet."""
    snippets = _load_snippets_or_exit()
    snippet = find_snippet(snippets, name)
    if snippet is None:
        _exit_with_error(f"No snippet named '{name}'")

    console.print(f"[bold cyan]{snippet.name}[/bold cyan]")
    console.print(f"[bold]Description:[/bold] {snippet.description or '-'}")
    console.print(f"[bold]Tags:[/bold] {', '.join(snippet.tags) or '-'}")
    console.print(f"[bold]Created:[/bold] {snippet.created_at}")
    console.print(f"[bold]Updated:[/bold] {snippet.updated_at}")
    console.print()
    console.print(Syntax(snippet.body, _guess_lexer(snippet), word_wrap=True))


@app.command("copy")
def copy_snippet(name: Annotated[str, typer.Argument(help="Snippet name to copy.")]) -> None:
    """Copy a snippet body to the clipboard."""
    snippets = _load_snippets_or_exit()
    snippet = find_snippet(snippets, name)
    if snippet is None:
        _exit_with_error(f"No snippet named '{name}'")

    try:
        copy_text(snippet.body)
    except ClipboardError as exc:
        _exit_with_error(str(exc))

    console.print(f"[green]Copied snippet to clipboard:[/green] {name}")


@app.command("list")
def list_snippets() -> None:
    """List all saved snippets."""
    snippets = _load_snippets_or_exit()
    if not snippets:
        console.print("[yellow]No snippets saved yet.[/yellow]")
        return

    _print_snippet_table(snippets, "Saved snippets")


@app.command()
def search(query: Annotated[str, typer.Argument(help="Search query.")]) -> None:
    """Search saved snippets."""
    snippets = _load_snippets_or_exit()
    matches = search_snippets(snippets, query)
    if not matches:
        console.print(f"[yellow]No snippets matched:[/yellow] {query}")
        return

    _print_snippet_table(matches, f"Search results for '{query}'")


@app.command()
def delete(name: Annotated[str, typer.Argument(help="Snippet name to delete.")]) -> None:
    """Delete a saved snippet."""
    snippets = _load_snippets_or_exit()
    snippet = find_snippet(snippets, name)
    if snippet is None:
        _exit_with_error(f"No snippet named '{name}'")

    should_delete = typer.confirm(f"Delete snippet '{name}'?", default=False)
    if not should_delete:
        console.print("[yellow]Cancelled.[/yellow]")
        return

    try:
        delete_snippet(name)
    except SnippetNotFoundError as exc:
        _exit_with_error(str(exc))
    except StorageCorruptionError as exc:
        _exit_with_error(str(exc))

    console.print(f"[green]Deleted snippet:[/green] {name}")


if __name__ == "__main__":
    app()
