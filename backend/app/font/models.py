from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FontItem:
    family: str
    display_name: str
    provider: str = "internal"
    weight: str = "400"
    italic: bool = False
    language: str = "vi"
    license: str = "open_font"
    local_path: str | None = None
    fallback: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class FontResolveRequest:
    family: str | None = None
    style_category: str | None = None
    language: str = "vi"
    weight: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)