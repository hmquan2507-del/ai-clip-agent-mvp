from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.review.editing.clipboard.models import (
    TimelineClipboardContent,
    TimelineClipboardState,
)
from app.review.editing.history.models import (
    TimelineHistoryState,
)
from app.review.editing.models import (
    EditableTimeline,
)
from app.review.models import ReviewWorkspace
from app.review.preview.models import (
    PreviewMediaSource,
    PreviewSessionState,
)
from app.review.selection.models import (
    TimelineSelectionCatalog,
    TimelineSelectionState,
)
from app.review.session.enums import (
    PreviewTimelineSyncStatus,
    ReviewRuntimeSessionEventType,
    ReviewRuntimeSessionStatus,
)


def utc_now_iso() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


@dataclass(frozen=True)
class PreviewTimelineSyncState:
    production_id: str
    status: PreviewTimelineSyncStatus
    active_timeline_revision: int

    preview_timeline_revision: int | None = None
    reason: str | None = None

    updated_at: str = field(
        default_factory=utc_now_iso
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def available(self) -> bool:
        return (
            self.status
            != PreviewTimelineSyncStatus.UNAVAILABLE
        )

    @property
    def current(self) -> bool:
        return (
            self.status
            == PreviewTimelineSyncStatus.CURRENT
        )

    @property
    def stale(self) -> bool:
        return (
            self.status
            == PreviewTimelineSyncStatus.STALE
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "status": self.status.value,
            "available": self.available,
            "current": self.current,
            "stale": self.stale,
            "active_timeline_revision": (
                self.active_timeline_revision
            ),
            "preview_timeline_revision": (
                self.preview_timeline_revision
            ),
            "reason": self.reason,
            "updated_at": self.updated_at,
            "metadata": deepcopy(
                self.metadata
            ),
        }


@dataclass(frozen=True)
class ReviewRuntimeSessionState:
    session_id: str
    production_id: str
    status: ReviewRuntimeSessionStatus

    timeline_revision: int
    dirty: bool = False
    revision: int = 1

    created_at: str = field(
        default_factory=utc_now_iso
    )
    updated_at: str = field(
        default_factory=utc_now_iso
    )
    closed_at: str | None = None

    error: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    @classmethod
    def create(
        cls,
        *,
        production_id: str,
        timeline_revision: int,
        dirty: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> ReviewRuntimeSessionState:
        return cls(
            session_id=str(uuid4()),
            production_id=production_id,
            status=(
                ReviewRuntimeSessionStatus
                .INITIALIZING
            ),
            timeline_revision=(
                timeline_revision
            ),
            dirty=dirty,
            metadata=deepcopy(
                metadata or {}
            ),
        )

    @property
    def active(self) -> bool:
        return self.status in {
            ReviewRuntimeSessionStatus
            .INITIALIZING,
            ReviewRuntimeSessionStatus.READY,
        }

    @property
    def ready(self) -> bool:
        return (
            self.status
            == ReviewRuntimeSessionStatus.READY
        )

    @property
    def closed(self) -> bool:
        return (
            self.status
            == ReviewRuntimeSessionStatus.CLOSED
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "production_id": self.production_id,
            "status": self.status.value,
            "active": self.active,
            "ready": self.ready,
            "closed": self.closed,
            "timeline_revision": (
                self.timeline_revision
            ),
            "dirty": self.dirty,
            "revision": self.revision,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "closed_at": self.closed_at,
            "error": self.error,
            "metadata": deepcopy(
                self.metadata
            ),
        }


@dataclass(frozen=True)
class ReviewRuntimeSessionSnapshot:
    session: ReviewRuntimeSessionState
    workspace: ReviewWorkspace
    timeline: EditableTimeline

    preview_source: PreviewMediaSource
    preview_state: PreviewSessionState
    preview_sync: PreviewTimelineSyncState

    selection_catalog: (
        TimelineSelectionCatalog
    )
    selection_state: TimelineSelectionState

    history_state: TimelineHistoryState
    clipboard_state: TimelineClipboardState
    clipboard_content: TimelineClipboardContent

    created_at: str = field(
        default_factory=utc_now_iso
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def session_id(self) -> str:
        return self.session.session_id

    @property
    def production_id(self) -> str:
        return self.session.production_id

    def clone(
        self,
    ) -> ReviewRuntimeSessionSnapshot:
        return deepcopy(self)

    def to_dict(self) -> dict[str, Any]:
        return deepcopy(
            {
                "session": (
                    self.session.to_dict()
                ),
                "workspace": (
                    self.workspace.to_dict()
                ),
                "timeline": (
                    self.timeline.to_dict()
                ),
                "preview": {
                    "source": (
                        self.preview_source
                        .to_dict()
                    ),
                    "state": (
                        self.preview_state
                        .to_dict()
                    ),
                    "sync": (
                        self.preview_sync
                        .to_dict()
                    ),
                },
                "selection": {
                    "catalog": (
                        self.selection_catalog
                        .to_dict()
                    ),
                    "state": (
                        self.selection_state
                        .to_dict()
                    ),
                },
                "history": (
                    self.history_state
                    .to_dict()
                ),
                "clipboard": {
                    "state": (
                        self.clipboard_state
                        .to_dict()
                    ),
                    "content": (
                        self.clipboard_content
                        .to_dict()
                    ),
                },
                "created_at": self.created_at,
                "metadata": self.metadata,
            }
        )


@dataclass(frozen=True)
class ReviewRuntimeSessionEvent:
    event_type: ReviewRuntimeSessionEventType
    session_id: str
    production_id: str

    session_revision: int
    timeline_revision: int

    created_at: str = field(
        default_factory=utc_now_iso
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type.value,
            "session_id": self.session_id,
            "production_id": self.production_id,
            "session_revision": (
                self.session_revision
            ),
            "timeline_revision": (
                self.timeline_revision
            ),
            "created_at": self.created_at,
            "metadata": deepcopy(
                self.metadata
            ),
        }


@dataclass(frozen=True)
class ReviewRuntimeSessionResult:
    success: bool
    state: ReviewRuntimeSessionState

    snapshot: (
        ReviewRuntimeSessionSnapshot | None
    ) = None
    event: ReviewRuntimeSessionEvent | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "state": self.state.to_dict(),
            "snapshot": (
                self.snapshot.to_dict()
                if self.snapshot
                else None
            ),
            "event": (
                self.event.to_dict()
                if self.event
                else None
            ),
            "error": self.error,
        }