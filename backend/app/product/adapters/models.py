from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.product.contracts import (
    ProductArtifactSummary,
    ProductProductionSnapshot,
)


@dataclass
class ProductTimelineSummary:
    available: bool
    version: str | int | None = None
    duration: float | None = None

    track_count: int = 0
    clip_count: int = 0
    effect_count: int = 0
    transition_count: int = 0

    canvas: dict[str, Any] = field(
        default_factory=dict
    )

    tracks: list[dict[str, Any]] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "available": self.available,
            "version": self.version,
            "duration": self.duration,
            "track_count": self.track_count,
            "clip_count": self.clip_count,
            "effect_count": self.effect_count,
            "transition_count": self.transition_count,
            "canvas": self.canvas,
            "tracks": self.tracks,
            "metadata": self.metadata,
        }


@dataclass
class ProductQualitySummary:
    available: bool
    approved: bool = False

    status: str | None = None
    quality_score: float | None = None

    warning_count: int = 0
    failure_count: int = 0

    report_path: str | None = None

    checks: list[dict[str, Any]] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "available": self.available,
            "approved": self.approved,
            "status": self.status,
            "quality_score": self.quality_score,
            "warning_count": self.warning_count,
            "failure_count": self.failure_count,
            "report_path": self.report_path,
            "checks": self.checks,
            "metadata": self.metadata,
        }


@dataclass
class ProductPreviewSummary:
    available: bool
    video_path: str | None = None
    video_url: str | None = None
    thumbnail_path: str | None = None
    thumbnail_url: str | None = None

    duration: float | None = None
    width: int | None = None
    height: int | None = None
    fps: float | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "available": self.available,
            "video_path": self.video_path,
            "video_url": self.video_url,
            "thumbnail_path": self.thumbnail_path,
            "thumbnail_url": self.thumbnail_url,
            "duration": self.duration,
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "metadata": self.metadata,
        }


@dataclass
class ProductWorkspaceSnapshot:
    production: ProductProductionSnapshot
    timeline: ProductTimelineSummary
    preview: ProductPreviewSummary
    quality: ProductQualitySummary

    artifacts: list[
        ProductArtifactSummary
    ] = field(default_factory=list)

    ai_summary: dict[str, Any] = field(
        default_factory=dict
    )

    issues: list[dict[str, Any]] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "production": self.production.to_dict(),
            "timeline": self.timeline.to_dict(),
            "preview": self.preview.to_dict(),
            "quality": self.quality.to_dict(),
            "artifacts": [
                item.to_dict()
                for item in self.artifacts
            ],
            "ai_summary": self.ai_summary,
            "issues": self.issues,
            "metadata": self.metadata,
        }