from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.review.editing.clipboard.enums import (
    TimelineClipboardAction,
    TimelineClipboardEventType,
    TimelineClipboardItemType,
    TimelineClipboardStatus,
)
from app.review.editing.models import (
    EditableTimelineClip,
)
from app.review.editing.history.models import (
    TimelineHistoryResult,
)

def utc_now_iso() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


@dataclass(frozen=True)
class TimelineClipboardItem:
    item_id: str
    item_type: TimelineClipboardItemType

    source_clip_id: str
    source_track_id: str

    clip: EditableTimelineClip

    relative_start: float
    relative_end: float

    source_order: int = 0

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def duration(self) -> float:
        return self.clip.duration

    def clone_clip(
        self,
    ) -> EditableTimelineClip:
        return self.clip.clone()

    def to_dict(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "item_type": self.item_type.value,
            "source_clip_id": (
                self.source_clip_id
            ),
            "source_track_id": (
                self.source_track_id
            ),
            "relative_start": (
                self.relative_start
            ),
            "relative_end": (
                self.relative_end
            ),
            "duration": self.duration,
            "source_order": (
                self.source_order
            ),
            "clip": self.clip.to_dict(),
            "metadata": deepcopy(
                self.metadata
            ),
        }


@dataclass(frozen=True)
class TimelineClipboardContent:
    clipboard_id: str
    production_id: str

    action: TimelineClipboardAction
    status: TimelineClipboardStatus

    items: tuple[
        TimelineClipboardItem,
        ...,
    ] = ()

    anchor_time: float = 0.0
    total_duration: float = 0.0

    created_at: str = field(
        default_factory=utc_now_iso
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    @classmethod
    def empty(
        cls,
        production_id: str,
    ) -> TimelineClipboardContent:
        return cls(
            clipboard_id=str(uuid4()),
            production_id=production_id,
            action=TimelineClipboardAction.COPY,
            status=TimelineClipboardStatus.EMPTY,
        )

    @property
    def available(self) -> bool:
        return bool(self.items)

    @property
    def item_count(self) -> int:
        return len(self.items)

    @property
    def clip_count(self) -> int:
        return sum(
            1
            for item in self.items
            if (
                item.item_type
                == TimelineClipboardItemType.CLIP
            )
        )

    @property
    def source_track_ids(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            dict.fromkeys(
                item.source_track_id
                for item in self.items
            )
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "clipboard_id": (
                self.clipboard_id
            ),
            "production_id": (
                self.production_id
            ),
            "action": self.action.value,
            "status": self.status.value,
            "available": self.available,
            "item_count": self.item_count,
            "clip_count": self.clip_count,
            "source_track_ids": list(
                self.source_track_ids
            ),
            "anchor_time": self.anchor_time,
            "total_duration": (
                self.total_duration
            ),
            "created_at": self.created_at,
            "items": [
                item.to_dict()
                for item in self.items
            ],
            "metadata": deepcopy(
                self.metadata
            ),
        }


@dataclass(frozen=True)
class TimelineClipboardEvent:
    event_type: TimelineClipboardEventType
    production_id: str

    clipboard_id: str | None = None
    item_count: int = 0

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
            "clipboard_id": (
                self.clipboard_id
            ),
            "item_count": self.item_count,
            "created_at": self.created_at,
            "metadata": deepcopy(
                self.metadata
            ),
        }


@dataclass(frozen=True)
class TimelineClipboardState:
    production_id: str
    status: TimelineClipboardStatus

    available: bool
    item_count: int
    clip_count: int

    clipboard_id: str | None = None
    last_action: (
        TimelineClipboardAction | None
    ) = None

    source_track_ids: tuple[
        str,
        ...,
    ] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": (
                self.production_id
            ),
            "status": self.status.value,
            "available": self.available,
            "item_count": self.item_count,
            "clip_count": self.clip_count,
            "clipboard_id": (
                self.clipboard_id
            ),
            "last_action": (
                self.last_action.value
                if self.last_action
                else None
            ),
            "source_track_ids": list(
                self.source_track_ids
            ),
        }


@dataclass(frozen=True)
class TimelineClipboardResult:
    success: bool

    content: TimelineClipboardContent
    state: TimelineClipboardState

    event: TimelineClipboardEvent | None = None

    timeline_history_result: (
        TimelineHistoryResult | None
    ) = None

    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
        "success": self.success,
        "content": self.content.to_dict(),
        "state": self.state.to_dict(),
        "event": (
            self.event.to_dict()
            if self.event
            else None
        ),
        "timeline_history_result": (
            self.timeline_history_result.to_dict()
            if self.timeline_history_result
            else None
        ),
        "error": self.error,
    }
    
@dataclass(frozen=True)
class TimelineClipboardHistoryEntry:
    entry_id: str
    content: TimelineClipboardContent

    created_at: str = field(
        default_factory=utc_now_iso
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    @classmethod
    def create(
        cls,
        content: TimelineClipboardContent,
    ) -> TimelineClipboardHistoryEntry:
        return cls(
            entry_id=str(uuid4()),
            content=content,
            metadata={
                "clipboard_id": (
                    content.clipboard_id
                ),
                "action": (
                    content.action.value
                ),
                "item_count": (
                    content.item_count
                ),
            },
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "created_at": self.created_at,
            "content": (
                self.content.to_dict()
            ),
            "metadata": deepcopy(
                self.metadata
            ),
        }


@dataclass(frozen=True)
class TimelineClipboardHistoryState:
    entry_count: int
    maximum_history_size: int

    latest_entry_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_count": self.entry_count,
            "maximum_history_size": (
                self.maximum_history_size
            ),
            "latest_entry_id": (
                self.latest_entry_id
            ),
        }