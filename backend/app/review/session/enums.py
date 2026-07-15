from __future__ import annotations

from enum import StrEnum


class ReviewRuntimeSessionStatus(StrEnum):
    INITIALIZING = "initializing"
    READY = "ready"
    CLOSED = "closed"
    ERROR = "error"


class PreviewTimelineSyncStatus(StrEnum):
    UNAVAILABLE = "unavailable"
    CURRENT = "current"
    STALE = "stale"


class ReviewRuntimeSessionEventType(StrEnum):
    SESSION_CREATED = "session_created"
    SESSION_READY = "session_ready"

    TIMELINE_CHANGED = "timeline_changed"

    SELECTION_CHANGED = (
        "selection_changed"
    )
    SELECTION_SYNCHRONIZED = (
        "selection_synchronized"
    )

    PREVIEW_MARKED_CURRENT = (
        "preview_marked_current"
    )
    PREVIEW_MARKED_STALE = (
        "preview_marked_stale"
    )

    SESSION_RESET = "session_reset"
    SESSION_CLOSED = "session_closed"
    SESSION_ERROR = "session_error"