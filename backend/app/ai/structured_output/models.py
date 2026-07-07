from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StructuredOutputResult:
    data: dict[str, Any]
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    raw_text: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "data": self.data,
            "is_valid": self.is_valid,
            "errors": self.errors,
            "raw_text": self.raw_text,
        }