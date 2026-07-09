from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MediaWorkflowRequest:
    query: str
    asset_type: str
    track_type: str | None = None
    preferred_duration: float | None = None
    preferred_orientation: str | None = None
    commercial_use: bool = True
    per_page: int = 5
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MediaWorkflowResult:
    workflow_key: str
    query: str
    asset_type: str
    provider_keys: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)