"""Clipboard helpers."""

from __future__ import annotations

import pyperclip


class ClipboardError(Exception):
    """Raised when text cannot be copied to the clipboard."""


def copy_text(text: str) -> None:
    try:
        pyperclip.copy(text)
    except pyperclip.PyperclipException as exc:
        raise ClipboardError("Could not copy text to the clipboard") from exc
