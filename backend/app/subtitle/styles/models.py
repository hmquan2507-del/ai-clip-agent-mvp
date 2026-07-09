from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SubtitleStyle:
    key: str
    name: str
    category: str
    font_family: str
    font_size: int
    font_weight: str = "700"
    text_color: str = "#FFFFFF"
    stroke_color: str = "#000000"
    stroke_width: int = 4
    shadow: bool = True
    highlight_color: str = "#FFD400"
    position: str = "bottom"
    animation: str = "pop"
    word_animation: str = "none"
    line_spacing: float = 1.0
    safe_margin: int = 80
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class SubtitleStyleResolveRequest:
    style_key: str | None = None
    category: str | None = None
    mood: str | None = None
    platform: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)