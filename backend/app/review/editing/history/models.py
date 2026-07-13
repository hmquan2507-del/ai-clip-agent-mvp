from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.review.editing.enums import (
    TimelineEditingOperationType,
)
from app.review.editing.history.enums import (
    TimelineHistoryAction,
    TimelineHistoryStatus,
)
from app.review.editing.models import (
    EditableTimeline,
    TimelineEditingEvent,
    TimelineMutationResult,
)


def utc_now_iso() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


@dataclass(frozen=True)
class TimelineHistoryCommand:
    command_id: str
    operation_type: TimelineEditingOperationType
    label: str

    before: EditableTimeline
    after: EditableTimeline

    editing_event: TimelineEditingEvent | None = None

    status: TimelineHistoryStatus = (
        TimelineHistoryStatus.APPLIED
    )

    created_at: str = field(
        default_factory=utc_now_iso
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    @classmethod
    def create(
        cls,
        *,
        operation_type: TimelineEditingOperationType,
        label: str,
        before: EditableTimeline,
        after: EditableTimeline,
        editing_event: TimelineEditingEvent | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> TimelineHistoryCommand:
        return cls(
            command_id=str(uuid4()),
            operation_type=operation_type,
            label=label,
            before=before.clone(),
            after=after.clone(),
            editing_event=editing_event,
            metadata=dict(metadata or {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "command_id": self.command_id,
            "operation_type": (
                self.operation_type.value
            ),
            "label": self.label,
            "status": self.status.value,
            "before_revision": (
                self.before.revision
            ),
            "after_revision": (
                self.after.revision
            ),
            "editing_event": (
                self.editing_event.to_dict()
                if self.editing_event
                else None
            ),
            "created_at": self.created_at,
            "metadata": deepcopy(
                self.metadata
            ),
        }


@dataclass(frozen=True)
class TimelineHistoryEvent:
    action: TimelineHistoryAction
    production_id: str

    command_id: str | None = None
    operation_type: (
        TimelineEditingOperationType | None
    ) = None

    undo_count: int = 0
    redo_count: int = 0

    created_at: str = field(
        default_factory=utc_now_iso
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action.value,
            "production_id": (
                self.production_id
            ),
            "command_id": self.command_id,
            "operation_type": (
                self.operation_type.value
                if self.operation_type
                else None
            ),
            "undo_count": self.undo_count,
            "redo_count": self.redo_count,
            "created_at": self.created_at,
            "metadata": deepcopy(
                self.metadata
            ),
        }


@dataclass(frozen=True)
class TimelineHistoryState:
    production_id: str

    can_undo: bool
    can_redo: bool

    undo_count: int
    redo_count: int

    current_revision: int
    maximum_history_size: int

    next_undo_label: str | None = None
    next_redo_label: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": (
                self.production_id
            ),
            "can_undo": self.can_undo,
            "can_redo": self.can_redo,
            "undo_count": self.undo_count,
            "redo_count": self.redo_count,
            "current_revision": (
                self.current_revision
            ),
            "maximum_history_size": (
                self.maximum_history_size
            ),
            "next_undo_label": (
                self.next_undo_label
            ),
            "next_redo_label": (
                self.next_redo_label
            ),
        }


@dataclass(frozen=True)
class TimelineHistoryResult:
    success: bool
    timeline: EditableTimeline
    state: TimelineHistoryState

    mutation_result: TimelineMutationResult | None = None
    command: TimelineHistoryCommand | None = None
    event: TimelineHistoryEvent | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "timeline": self.timeline.to_dict(),
            "state": self.state.to_dict(),
            "mutation_result": (
                self.mutation_result.to_dict()
                if self.mutation_result
                else None
            ),
            "command": (
                self.command.to_dict()
                if self.command
                else None
            ),
            "event": (
                self.event.to_dict()
                if self.event
                else None
            ),
            "error": self.error,
        }