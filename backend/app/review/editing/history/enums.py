from __future__ import annotations

from enum import StrEnum


class TimelineHistoryAction(StrEnum):
    EXECUTE = "execute"
    UNDO = "undo"
    REDO = "redo"
    CLEAR = "clear"
    RESET = "reset"


class TimelineHistoryStatus(StrEnum):
    READY = "ready"
    APPLIED = "applied"
    UNDONE = "undone"
    REDONE = "redone"
    FAILED = "failed"