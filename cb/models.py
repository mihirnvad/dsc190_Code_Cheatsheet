"""Data models for Code Boilerplate Vault."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


def utc_now_iso() -> str:
    """Return an ISO-8601 timestamp in UTC."""
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Snippet:
    """A saved code snippet or command template."""

    name: str
    description: str = ""
    tags: List[str] = field(default_factory=list)
    body: str = ""
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Snippet":
        return cls(
            name=str(data.get("name", "")),
            description=str(data.get("description", "")),
            tags=[str(tag) for tag in data.get("tags", [])],
            body=str(data.get("body", "")),
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", "")),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "body": self.body,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
