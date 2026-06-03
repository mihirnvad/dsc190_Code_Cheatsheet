"""Typer CLI entry point for Code Boilerplate Vault."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console

from cb.storage import init_storage

app = typer.Typer(
    help="Code Boilerplate Vault: save, find, and reuse code snippets from the terminal."
)
console = Console()


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
    _ = (name, tag, description)
    console.print("[yellow]TODO:[/yellow] implement editor-backed snippet creation.")


@app.command()
def get(name: Annotated[str, typer.Argument(help="Snippet name to print.")]) -> None:
    """Print a saved snippet."""
    _ = name
    console.print("[yellow]TODO:[/yellow] implement snippet lookup and printing.")


@app.command("copy")
def copy_snippet(name: Annotated[str, typer.Argument(help="Snippet name to copy.")]) -> None:
    """Copy a snippet body to the clipboard."""
    _ = name
    console.print("[yellow]TODO:[/yellow] implement clipboard copying.")


@app.command("list")
def list_snippets() -> None:
    """List all saved snippets."""
    console.print("[yellow]TODO:[/yellow] implement snippet table output.")


@app.command()
def search(query: Annotated[str, typer.Argument(help="Search query.")]) -> None:
    """Search saved snippets."""
    _ = query
    console.print("[yellow]TODO:[/yellow] implement snippet search output.")


@app.command()
def delete(name: Annotated[str, typer.Argument(help="Snippet name to delete.")]) -> None:
    """Delete a saved snippet."""
    _ = name
    console.print("[yellow]TODO:[/yellow] implement snippet deletion.")


if __name__ == "__main__":
    app()
