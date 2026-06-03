import pyperclip
import pytest

from cb import clipboard
from cb.clipboard import ClipboardError, copy_text


def test_copy_text_delegates_to_pyperclip(monkeypatch) -> None:
    copied_text = []
    monkeypatch.setattr(clipboard.pyperclip, "copy", copied_text.append)

    copy_text("git status\n")

    assert copied_text == ["git status\n"]


def test_copy_text_reports_pyperclip_failure(monkeypatch) -> None:
    def fail_copy(text: str) -> None:
        raise pyperclip.PyperclipException("no clipboard")

    monkeypatch.setattr(clipboard.pyperclip, "copy", fail_copy)

    with pytest.raises(ClipboardError):
        copy_text("git status\n")
