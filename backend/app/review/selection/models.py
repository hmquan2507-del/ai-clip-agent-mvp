from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.review.selection.enums import (
    TimelineSelectionEventType,
    TimelineSelectionFocus,
    TimelineSelectionMode,
)


def utc_now_iso() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


@dataclass(frozen=True)
class TimelineSelectableClip:
    clip_id: str
    track_id: str

    start_time: float
    end_time: float

    clip_type: str | None = None
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        start_time = max(
            0.0,
            float(self.start_time),
        )

        end_time = max(
            start_time,
            float(self.end_time),
        )

        object.__setattr__(
            self,
            "start_time",
            start_time,
        )

        object.__setattr__(
            self,
            "end_time",
            end_time,
        )

    @property
    def duration(self) -> float:
        return max(
            0.0,
            self.end_time - self.start_time,
        )

    def contains_time(
        self,
        value: float,
    ) -> bool:
        time_value = float(value)

        return (
            self.start_time
            <= time_value
            <= self.end_time
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "clip_id": self.clip_id,
            "track_id": self.track_id,
            "clip_type": self.clip_type,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class TimelineSelectableTrack:
    track_id: str

    track_type: str | None = None
    name: str | None = None
    position: int = 0

    clip_ids: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "track_id": self.track_id,
            "track_type": self.track_type,
            "name": self.name,
            "position": self.position,
            "clip_ids": list(
                self.clip_ids
            ),
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class TimelineSelectionCatalog:
    production_id: str
    duration: float

    tracks: tuple[
        TimelineSelectableTrack,
        ...,
    ] = ()

    clips: tuple[
        TimelineSelectableClip,
        ...,
    ] = ()

    fps: float = 30.0

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "duration",
            max(
                0.0,
                float(self.duration),
            ),
        )

        fps = float(self.fps)

        if fps <= 0:
            fps = 30.0

        object.__setattr__(
            self,
            "fps",
            fps,
        )

    @property
    def track_ids(self) -> set[str]:
        return {
            item.track_id
            for item in self.tracks
        }

    @property
    def clip_ids(self) -> set[str]:
        return {
            item.clip_id
            for item in self.clips
        }

    def get_track(
        self,
        track_id: str,
    ) -> TimelineSelectableTrack | None:
        return next(
            (
                item
                for item in self.tracks
                if item.track_id == track_id
            ),
            None,
        )

    def get_clip(
        self,
        clip_id: str,
    ) -> TimelineSelectableClip | None:
        return next(
            (
                item
                for item in self.clips
                if item.clip_id == clip_id
            ),
            None,
        )

    def clips_at_time(
        self,
        value: float,
    ) -> list[TimelineSelectableClip]:
        return [
            item
            for item in self.clips
            if item.contains_time(value)
        ]

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": (
                self.production_id
            ),
            "duration": self.duration,
            "fps": self.fps,
            "track_count": len(
                self.tracks
            ),
            "clip_count": len(
                self.clips
            ),
            "tracks": [
                item.to_dict()
                for item in self.tracks
            ],
            "clips": [
                item.to_dict()
                for item in self.clips
            ],
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class TimelineTimeRange:
    start_time: float
    end_time: float

    def __post_init__(self) -> None:
        start = float(self.start_time)
        end = float(self.end_time)

        if end < start:
            start, end = end, start

        object.__setattr__(
            self,
            "start_time",
            max(0.0, start),
        )

        object.__setattr__(
            self,
            "end_time",
            max(0.0, end),
        )

    @property
    def duration(self) -> float:
        return max(
            0.0,
            self.end_time - self.start_time,
        )

    def to_dict(self) -> dict[str, float]:
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
        }


@dataclass
class TimelineSelectionState:
    production_id: str

    mode: TimelineSelectionMode = (
        TimelineSelectionMode.NONE
    )

    focus: TimelineSelectionFocus = (
        TimelineSelectionFocus.TIMELINE
    )

    selected_track_ids: list[str] = field(
        default_factory=list
    )

    selected_clip_ids: list[str] = field(
        default_factory=list
    )

    active_track_id: str | None = None
    active_clip_id: str | None = None

    hovered_track_id: str | None = None
    hovered_clip_id: str | None = None

    cursor_time: float = 0.0
    cursor_frame: int = 0

    selected_range: (
        TimelineTimeRange | None
    ) = None

    revision: int = 1

    created_at: str = field(
        default_factory=utc_now_iso
    )

    updated_at: str = field(
        default_factory=utc_now_iso
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def has_selection(self) -> bool:
        return bool(
            self.selected_track_ids
            or self.selected_clip_ids
            or self.selected_range
        )

    @property
    def selected_count(self) -> int:
        return (
            len(self.selected_track_ids)
            + len(self.selected_clip_ids)
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": (
                self.production_id
            ),
            "mode": self.mode.value,
            "focus": self.focus.value,
            "selected_track_ids": list(
                self.selected_track_ids
            ),
            "selected_clip_ids": list(
                self.selected_clip_ids
            ),
            "active_track_id": (
                self.active_track_id
            ),
            "active_clip_id": (
                self.active_clip_id
            ),
            "hovered_track_id": (
                self.hovered_track_id
            ),
            "hovered_clip_id": (
                self.hovered_clip_id
            ),
            "cursor_time": self.cursor_time,
            "cursor_frame": (
                self.cursor_frame
            ),
            "selected_range": (
                self.selected_range.to_dict()
                if self.selected_range
                else None
            ),
            "has_selection": (
                self.has_selection
            ),
            "selected_count": (
                self.selected_count
            ),
            "revision": self.revision,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class TimelineSelectionEvent:
    event_type: TimelineSelectionEventType
    production_id: str
    state_revision: int

    created_at: str = field(
        default_factory=utc_now_iso
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": (
                self.event_type.value
            ),
            "production_id": (
                self.production_id
            ),
            "state_revision": (
                self.state_revision
            ),
            "created_at": self.created_at,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class TimelineSelectionResult:
    success: bool
    state: TimelineSelectionState

    event: TimelineSelectionEvent | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "state": self.state.to_dict(),
            "event": (
                self.event.to_dict()
                if self.event
                else None
            ),
            "error": self.error,
        }