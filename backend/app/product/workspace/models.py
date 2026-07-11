from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.product.adapters import (
    ProductWorkspaceSnapshot,
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ProductWorkspaceSources:
    production: Any
    timeline: Any | None = None
    artifacts: list[Any] = field(
        default_factory=list
    )
    quality_report: Any | None = None
    ai_summary: dict[str, Any] = field(
        default_factory=dict
    )
    issues: list[Any] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class ProductWorkspaceLoadResult:
    production_id: str
    success: bool

    snapshot: ProductWorkspaceSnapshot | None

    cache_hit: bool = False
    loaded_at: str = field(
        default_factory=utc_now_iso
    )

    errors: list[str] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "success": self.success,
            "snapshot": (
                self.snapshot.to_dict()
                if self.snapshot
                else None
            ),
            "cache_hit": self.cache_hit,
            "loaded_at": self.loaded_at,
            "errors": list(self.errors),
            "metadata": self.metadata,
        }