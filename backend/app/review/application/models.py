from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.review.editing.clipboard.models import (
    TimelineClipboardHistoryEntry,
    TimelineClipboardHistoryState,
    TimelineClipboardResult,
)
from app.review.editing.history.models import (
    TimelineHistoryResult,
)
from app.review.session.models import (
    ReviewRuntimeSessionSnapshot,
)


class ReviewTimelineCommandType(str, Enum):
    MOVE_CLIP = "move_clip"
    TRIM_CLIP_START = "trim_clip_start"
    TRIM_CLIP_END = "trim_clip_end"
    SPLIT_CLIP = "split_clip"
    DUPLICATE_CLIP = "duplicate_clip"
    DELETE_CLIP = "delete_clip"
    CLOSE_GAP = "close_gap"
    MOVE_CLIPS = "move_clips"
    DUPLICATE_CLIPS = "duplicate_clips"
    DELETE_CLIPS = "delete_clips"
    UNDO = "undo"
    REDO = "redo"


class ReviewClipboardCommandType(
    str,
    Enum,
):
    COPY = "copy"
    CUT = "cut"
    PASTE = "paste"

    RESTORE_HISTORY = (
        "restore_history"
    )

    CLEAR_CONTENT = (
        "clear_content"
    )

    CLEAR_HISTORY = (
        "clear_history"
    )


@dataclass(frozen=True)
class ReviewTimelineCommandResult:
    operation: ReviewTimelineCommandType

    production_id: str
    session_id: str

    previous_revision: int
    current_revision: int

    snapshot: ReviewRuntimeSessionSnapshot
    history_result: TimelineHistoryResult

    expected_revision: int | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        operation = self.operation

        if not isinstance(
            operation,
            ReviewTimelineCommandType,
        ):
            operation = (
                ReviewTimelineCommandType(
                    str(operation)
                )
            )

        production_id = str(
            self.production_id
        ).strip()

        session_id = str(
            self.session_id
        ).strip()

        if not production_id:
            raise ValueError(
                "production_id is required."
            )

        if not session_id:
            raise ValueError(
                "session_id is required."
            )

        previous_revision = int(
            self.previous_revision
        )

        current_revision = int(
            self.current_revision
        )

        if previous_revision < 1:
            raise ValueError(
                "previous_revision must be "
                "greater than or equal to 1."
            )

        if current_revision < 1:
            raise ValueError(
                "current_revision must be "
                "greater than or equal to 1."
            )

        expected_revision = (
            int(self.expected_revision)
            if self.expected_revision
            is not None
            else None
        )

        if (
            expected_revision is not None
            and expected_revision < 1
        ):
            raise ValueError(
                "expected_revision must be "
                "greater than or equal to 1."
            )

        if not self.history_result.success:
            raise ValueError(
                "A successful timeline command "
                "result requires a successful "
                "history result."
            )

        if (
            self.snapshot.production_id
            != production_id
        ):
            raise ValueError(
                "Timeline command snapshot "
                "production_id does not match."
            )

        if (
            self.snapshot.session_id
            != session_id
        ):
            raise ValueError(
                "Timeline command snapshot "
                "session_id does not match."
            )

        if (
            self.snapshot.timeline.revision
            != current_revision
        ):
            raise ValueError(
                "Timeline command snapshot "
                "revision does not match "
                "current_revision."
            )

        object.__setattr__(
            self,
            "operation",
            operation,
        )

        object.__setattr__(
            self,
            "production_id",
            production_id,
        )

        object.__setattr__(
            self,
            "session_id",
            session_id,
        )

        object.__setattr__(
            self,
            "previous_revision",
            previous_revision,
        )

        object.__setattr__(
            self,
            "current_revision",
            current_revision,
        )

        object.__setattr__(
            self,
            "expected_revision",
            expected_revision,
        )

        object.__setattr__(
            self,
            "snapshot",
            self.snapshot.clone(),
        )

        object.__setattr__(
            self,
            "history_result",
            deepcopy(
                self.history_result
            ),
        )

        object.__setattr__(
            self,
            "metadata",
            deepcopy(
                self.metadata
            ),
        )

    @property
    def command(
        self,
    ) -> dict[str, Any] | None:
        command = (
            self.history_result.command
        )

        return (
            deepcopy(
                command.to_dict()
            )
            if command is not None
            else None
        )

    @property
    def event(
        self,
    ) -> dict[str, Any] | None:
        event = (
            self.history_result.event
        )

        return (
            deepcopy(
                event.to_dict()
            )
            if event is not None
            else None
        )

    @property
    def history(
        self,
    ) -> dict[str, Any]:
        return deepcopy(
            self.history_result
            .state.to_dict()
        )

    def clone(
        self,
    ) -> ReviewTimelineCommandResult:
        return deepcopy(self)

    def to_dict(self) -> dict[str, Any]:
        return deepcopy(
            {
                "operation": (
                    self.operation.value
                ),
                "production_id": (
                    self.production_id
                ),
                "session_id": (
                    self.session_id
                ),
                "previous_revision": (
                    self.previous_revision
                ),
                "current_revision": (
                    self.current_revision
                ),
                "expected_revision": (
                    self.expected_revision
                ),
                "snapshot": (
                    self.snapshot.to_dict()
                ),
                "command": self.command,
                "event": self.event,
                "history": self.history,
                "metadata": self.metadata,
            }
        )


@dataclass(frozen=True)
class ReviewClipboardCommandResult:
    operation: ReviewClipboardCommandType

    production_id: str
    session_id: str

    previous_revision: int
    current_revision: int

    snapshot: ReviewRuntimeSessionSnapshot

    clipboard_result:TimelineClipboardResult

    clipboard_history_state:TimelineClipboardHistoryState

    clipboard_history_entries: tuple[
        TimelineClipboardHistoryEntry,
        ...,
    ] = field(
        default_factory=tuple
    )

    expected_revision: int | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        operation = self.operation

        if not isinstance(
            operation,
            ReviewClipboardCommandType,
        ):
            operation = (
                ReviewClipboardCommandType(
                    str(operation)
                )
            )

        production_id = str(
            self.production_id
        ).strip()

        session_id = str(
            self.session_id
        ).strip()

        if not production_id:
            raise ValueError(
                "production_id is required."
            )

        if not session_id:
            raise ValueError(
                "session_id is required."
            )

        previous_revision = int(
            self.previous_revision
        )

        current_revision = int(
            self.current_revision
        )

        if previous_revision < 1:
            raise ValueError(
                "previous_revision must be "
                "greater than or equal to 1."
            )

        if current_revision < 1:
            raise ValueError(
                "current_revision must be "
                "greater than or equal to 1."
            )

        expected_revision = (
            int(self.expected_revision)
            if self.expected_revision
            is not None
            else None
        )

        if (
            expected_revision is not None
            and expected_revision < 1
        ):
            raise ValueError(
                "expected_revision must be "
                "greater than or equal to 1."
            )

        if not self.clipboard_result.success:
            raise ValueError(
                "A successful clipboard command "
                "result requires a successful "
                "clipboard runtime result."
            )

        if (
            self.snapshot.production_id
            != production_id
        ):
            raise ValueError(
                "Clipboard command snapshot "
                "production_id does not match."
            )

        if (
            self.snapshot.session_id
            != session_id
        ):
            raise ValueError(
                "Clipboard command snapshot "
                "session_id does not match."
            )

        if (
            self.snapshot.timeline.revision
            != current_revision
        ):
            raise ValueError(
                "Clipboard command snapshot "
                "revision does not match "
                "current_revision."
            )

        clipboard_state = (
            self.clipboard_result.state
        )

        clipboard_content = (
            self.clipboard_result.content
        )

        if (
            clipboard_state.production_id
            != production_id
        ):
            raise ValueError(
                "Clipboard state production_id "
                "does not match."
            )

        if (
            clipboard_content.production_id
            != production_id
        ):
            raise ValueError(
                "Clipboard content production_id "
                "does not match."
            )

        history_entries = tuple(
            deepcopy(
                self.clipboard_history_entries
            )
        )

        history_state = deepcopy(
            self.clipboard_history_state
        )

        if (
            history_state.entry_count
            != len(history_entries)
        ):
            raise ValueError(
                "Clipboard history state "
                "entry_count does not match "
                "clipboard_history_entries."
            )

        object.__setattr__(
            self,
            "operation",
            operation,
        )

        object.__setattr__(
            self,
            "production_id",
            production_id,
        )

        object.__setattr__(
            self,
            "session_id",
            session_id,
        )

        object.__setattr__(
            self,
            "previous_revision",
            previous_revision,
        )

        object.__setattr__(
            self,
            "current_revision",
            current_revision,
        )

        object.__setattr__(
            self,
            "expected_revision",
            expected_revision,
        )

        object.__setattr__(
            self,
            "snapshot",
            self.snapshot.clone(),
        )

        object.__setattr__(
            self,
            "clipboard_result",
            deepcopy(
                self.clipboard_result
            ),
        )

        object.__setattr__(
            self,
            "clipboard_history_state",
            history_state,
        )

        object.__setattr__(
            self,
            "clipboard_history_entries",
            history_entries,
        )

        object.__setattr__(
            self,
            "metadata",
            deepcopy(
                self.metadata
            ),
        )

    @property
    def timeline_changed(
        self,
    ) -> bool:
        return (
            self.previous_revision
            != self.current_revision
        )

    @property
    def clipboard(
        self,
    ) -> dict[str, Any]:
        return deepcopy(
            {
                "state": (
                    self.clipboard_result
                    .state.to_dict()
                ),
                "content": (
                    self.clipboard_result
                    .content.to_dict()
                ),
                "event": (
                    self.clipboard_result
                    .event.to_dict()
                    if self.clipboard_result
                    .event
                    else None
                ),
                "history_state": (
                    self.clipboard_history_state
                    .to_dict()
                ),
                "history": [
                    entry.to_dict()
                    for entry
                    in self
                    .clipboard_history_entries
                ],
            }
        )

    @property
    def timeline_history(
        self,
    ) -> dict[str, Any] | None:
        history_result = (
            self.clipboard_result
            .timeline_history_result
        )

        return (
            deepcopy(
                history_result.to_dict()
            )
            if history_result is not None
            else None
        )

    def clone(
        self,
    ) -> ReviewClipboardCommandResult:
        return deepcopy(self)

    def to_dict(self) -> dict[str, Any]:
        return deepcopy(
            {
                "operation": (
                    self.operation.value
                ),
                "production_id": (
                    self.production_id
                ),
                "session_id": (
                    self.session_id
                ),
                "previous_revision": (
                    self.previous_revision
                ),
                "current_revision": (
                    self.current_revision
                ),
                "expected_revision": (
                    self.expected_revision
                ),
                "timeline_changed": (
                    self.timeline_changed
                ),
                "snapshot": (
                    self.snapshot.to_dict()
                ),
                "clipboard": (
                    self.clipboard
                ),
                "timeline_history": (
                    self.timeline_history
                ),
                "metadata": (
                    self.metadata
                ),
            }
        )
    
    
