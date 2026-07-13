from __future__ import annotations
import json
from dataclasses import asdict, dataclass, field
from typing import Any

@dataclass(frozen=True)
class PreviewState:
    """
    Represents the state of the rendered preview video.
    """
    available: bool = False
    video_url: str | None = None
    thumbnail_url: str | None = None
    duration: float | None = None
    width: int | None = None
    height: int | None = None
    fps: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class TimelineState:
    """
    Represents the state of the timeline.
    """
    version: str | int | None = None
    duration: float | None = None
    track_count: int = 0
    clip_count: int = 0
    tracks: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class ReviewState:
    """
    Represents the state of the review process.
    """
    is_approved: bool = False
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class ExportState:
    """
    Represents the state of the final export.
    """
    is_exported: bool = False
    export_url: str | None = None
    export_format: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class AIState:
    """
    Represents the state of AI-related suggestions and metadata.
    """
    suggestions: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class SelectionState:
    """
    Represents the state of the user's selection in the UI.
    """
    selected_clip_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class ReviewWorkspace:
    """
    Represents the entire state of the Review Workspace.
    """
    production_id: str
    version: int
    preview: PreviewState
    timeline: TimelineState
    review: ReviewState
    export: ExportState
    ai: AIState
    selection: SelectionState
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "version": self.version,
            "preview": self.preview.to_dict(),
            "timeline": self.timeline.to_dict(),
            "review": self.review.to_dict(),
            "export": self.export.to_dict(),
            "ai": self.ai.to_dict(),
            "selection": self.selection.to_dict(),
            "metadata": self.metadata,
        }

    def to_json(self, indent: int | None = 4) -> str:
        return json.dumps(self.to_dict(), indent=indent)
