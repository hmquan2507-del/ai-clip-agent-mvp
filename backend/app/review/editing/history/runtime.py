from __future__ import annotations

from typing import Any, Callable

from app.review.editing.enums import (
    TimelineEditingOperationType,
)
from app.review.editing.history.enums import (
    TimelineHistoryAction,
)
from app.review.editing.history.models import (
    TimelineHistoryCommand,
    TimelineHistoryEvent,
    TimelineHistoryResult,
    TimelineHistoryState,
)
from app.review.editing.models import (
    EditableTimeline,
    EditableTimelineClip,
    TimelineMutationResult,
)
from app.review.editing.runtime import (
    TimelineMutationRuntime,
)


MutationCallable = Callable[
    [],
    TimelineMutationResult,
]


class TimelineCommandHistoryRuntime:
    def __init__(
        self,
        mutation_runtime: TimelineMutationRuntime,
        *,
        maximum_history_size: int = 100,
    ):
        self.mutation_runtime = (
            mutation_runtime
        )

        self.maximum_history_size = max(
            1,
            int(maximum_history_size),
        )

        self._initial_timeline = (
            mutation_runtime.snapshot()
        )

        self._undo_stack: list[
            TimelineHistoryCommand
        ] = []

        self._redo_stack: list[
            TimelineHistoryCommand
        ] = []

        self._events: list[
            TimelineHistoryEvent
        ] = []

    @property
    def timeline(self) -> EditableTimeline:
        return self.mutation_runtime.snapshot()

    @property
    def can_undo(self) -> bool:
        return bool(self._undo_stack)

    @property
    def can_redo(self) -> bool:
        return bool(self._redo_stack)

    @property
    def undo_commands(
        self,
    ) -> list[TimelineHistoryCommand]:
        return list(self._undo_stack)

    @property
    def redo_commands(
        self,
    ) -> list[TimelineHistoryCommand]:
        return list(self._redo_stack)

    @property
    def events(
        self,
    ) -> list[TimelineHistoryEvent]:
        return list(self._events)

    def state(self) -> TimelineHistoryState:
        timeline = self.timeline

        return TimelineHistoryState(
            production_id=(
                timeline.production_id
            ),
            can_undo=self.can_undo,
            can_redo=self.can_redo,
            undo_count=len(
                self._undo_stack
            ),
            redo_count=len(
                self._redo_stack
            ),
            current_revision=(
                timeline.revision
            ),
            maximum_history_size=(
                self.maximum_history_size
            ),
            next_undo_label=(
                self._undo_stack[-1].label
                if self._undo_stack
                else None
            ),
            next_redo_label=(
                self._redo_stack[-1].label
                if self._redo_stack
                else None
            ),
        )

    def execute(
        self,
        *,
        operation_type: TimelineEditingOperationType,
        label: str,
        mutation: MutationCallable,
        metadata: dict[str, Any] | None = None,
    ) -> TimelineHistoryResult:
        before = self.timeline

        try:
            mutation_result = mutation()
        except Exception as error:
            return self._failure(
                str(error)
            )

        if not mutation_result.success:
            return TimelineHistoryResult(
                success=False,
                timeline=self.timeline,
                state=self.state(),
                mutation_result=(
                    mutation_result
                ),
                error=mutation_result.error,
            )

        after = self.timeline

        command = TimelineHistoryCommand.create(
            operation_type=operation_type,
            label=label,
            before=before,
            after=after,
            editing_event=(
                mutation_result.event
            ),
            metadata=metadata,
        )

        self._undo_stack.append(
            command
        )

        self._trim_undo_stack()

        # Một edit mới sau undo phải xóa
        # toàn bộ nhánh redo cũ.
        self._redo_stack.clear()

        event = self._emit(
            action=(
                TimelineHistoryAction.EXECUTE
            ),
            command=command,
        )

        return TimelineHistoryResult(
            success=True,
            timeline=self.timeline,
            state=self.state(),
            mutation_result=(
                mutation_result
            ),
            command=command,
            event=event,
        )

    def undo(self) -> TimelineHistoryResult:
        if not self._undo_stack:
            return self._failure(
                "Không còn thao tác để hoàn tác."
            )

        command = self._undo_stack.pop()

        self.mutation_runtime.replace_timeline(
            command.before
        )

        self._redo_stack.append(
            command
        )

        event = self._emit(
            action=TimelineHistoryAction.UNDO,
            command=command,
        )

        return TimelineHistoryResult(
            success=True,
            timeline=self.timeline,
            state=self.state(),
            command=command,
            event=event,
        )

    def redo(self) -> TimelineHistoryResult:
        if not self._redo_stack:
            return self._failure(
                "Không còn thao tác để làm lại."
            )

        command = self._redo_stack.pop()

        self.mutation_runtime.replace_timeline(
            command.after
        )

        self._undo_stack.append(
            command
        )

        self._trim_undo_stack()

        event = self._emit(
            action=TimelineHistoryAction.REDO,
            command=command,
        )

        return TimelineHistoryResult(
            success=True,
            timeline=self.timeline,
            state=self.state(),
            command=command,
            event=event,
        )

    def clear_history(
        self,
    ) -> TimelineHistoryResult:
        self._undo_stack.clear()
        self._redo_stack.clear()

        event = self._emit(
            action=TimelineHistoryAction.CLEAR
        )

        return TimelineHistoryResult(
            success=True,
            timeline=self.timeline,
            state=self.state(),
            event=event,
        )

    def reset(
        self,
    ) -> TimelineHistoryResult:
        self.mutation_runtime.replace_timeline(
            self._initial_timeline,
            clear_events=True,
        )

        self._undo_stack.clear()
        self._redo_stack.clear()

        event = self._emit(
            action=TimelineHistoryAction.RESET
        )

        return TimelineHistoryResult(
            success=True,
            timeline=self.timeline,
            state=self.state(),
            event=event,
        )

    # Convenience commands

    def move_clip(
        self,
        clip_id: str,
        new_start_time: float,
        *,
        target_track_id: str | None = None,
    ) -> TimelineHistoryResult:
        return self.execute(
            operation_type=(
                TimelineEditingOperationType
                .MOVE_CLIP
            ),
            label="Di chuyển clip",
            mutation=lambda: (
                self.mutation_runtime.move_clip(
                    clip_id,
                    new_start_time,
                    target_track_id=(
                        target_track_id
                    ),
                )
            ),
            metadata={
                "clip_id": clip_id,
            },
        )

    def trim_clip_start(
        self,
        clip_id: str,
        new_start_time: float,
    ) -> TimelineHistoryResult:
        return self.execute(
            operation_type=(
                TimelineEditingOperationType
                .TRIM_CLIP_START
            ),
            label="Cắt đầu clip",
            mutation=lambda: (
                self.mutation_runtime
                .trim_clip_start(
                    clip_id,
                    new_start_time,
                )
            ),
            metadata={
                "clip_id": clip_id,
            },
        )

    def trim_clip_end(
        self,
        clip_id: str,
        new_end_time: float,
    ) -> TimelineHistoryResult:
        return self.execute(
            operation_type=(
                TimelineEditingOperationType
                .TRIM_CLIP_END
            ),
            label="Cắt cuối clip",
            mutation=lambda: (
                self.mutation_runtime
                .trim_clip_end(
                    clip_id,
                    new_end_time,
                )
            ),
            metadata={
                "clip_id": clip_id,
            },
        )

    def insert_clip(
        self,
        track_id: str,
        clip: EditableTimelineClip,
    ) -> TimelineHistoryResult:
        return self.execute(
            operation_type=(
                TimelineEditingOperationType
                .INSERT_CLIP
            ),
            label="Thêm clip",
            mutation=lambda: (
                self.mutation_runtime
                .insert_clip(
                    track_id,
                    clip,
                )
            ),
            metadata={
                "track_id": track_id,
                "clip_id": clip.clip_id,
            },
        )

    def split_clip(
        self,
        clip_id: str,
        split_time: float,
        *,
        right_clip_id: str | None = None,
    ) -> TimelineHistoryResult:
        return self.execute(
            operation_type=(
                TimelineEditingOperationType
                .SPLIT_CLIP
            ),
            label="Chia clip",
            mutation=lambda: (
                self.mutation_runtime
                .split_clip(
                    clip_id,
                    split_time,
                    right_clip_id=(
                        right_clip_id
                    ),
                )
            ),
            metadata={
                "clip_id": clip_id,
            },
        )

    def duplicate_clip(
        self,
        clip_id: str,
        *,
        new_clip_id: str | None = None,
        new_start_time: float | None = None,
        target_track_id: str | None = None,
    ) -> TimelineHistoryResult:
        return self.execute(
            operation_type=(
                TimelineEditingOperationType
                .DUPLICATE_CLIP
            ),
            label="Nhân bản clip",
            mutation=lambda: (
                self.mutation_runtime
                .duplicate_clip(
                    clip_id,
                    new_clip_id=(
                        new_clip_id
                    ),
                    new_start_time=(
                        new_start_time
                    ),
                    target_track_id=(
                        target_track_id
                    ),
                )
            ),
            metadata={
                "clip_id": clip_id,
            },
        )

    def delete_clip(
        self,
        clip_id: str,
        *,
        close_gap: bool = False,
    ) -> TimelineHistoryResult:
        return self.execute(
            operation_type=(
                TimelineEditingOperationType
                .DELETE_CLIP
            ),
            label="Xóa clip",
            mutation=lambda: (
                self.mutation_runtime
                .delete_clip(
                    clip_id,
                    close_gap=close_gap,
                )
            ),
            metadata={
                "clip_id": clip_id,
                "close_gap": close_gap,
            },
        )

    def close_gap(
        self,
        track_id: str,
        gap_start: float,
        gap_end: float,
    ) -> TimelineHistoryResult:
        return self.execute(
            operation_type=(
                TimelineEditingOperationType
                .CLOSE_GAP
            ),
            label="Đóng khoảng trống",
            mutation=lambda: (
                self.mutation_runtime
                .close_gap(
                    track_id,
                    gap_start,
                    gap_end,
                )
            ),
            metadata={
                "track_id": track_id,
            },
        )

    def close_all_gaps(
        self,
        track_id: str,
    ) -> TimelineHistoryResult:
        return self.execute(
            operation_type=(
                TimelineEditingOperationType
                .CLOSE_GAP
            ),
            label="Đóng mọi khoảng trống",
            mutation=lambda: (
                self.mutation_runtime
                .close_all_gaps(
                    track_id
                )
            ),
            metadata={
                "track_id": track_id,
                "close_all": True,
            },
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "timeline": self.timeline.to_dict(),
            "state": self.state().to_dict(),
            "undo_stack": [
                command.to_dict()
                for command
                in self._undo_stack
            ],
            "redo_stack": [
                command.to_dict()
                for command
                in self._redo_stack
            ],
            "events": [
                event.to_dict()
                for event in self._events
            ],
            "metadata": {
                "runtime": (
                    "TimelineCommandHistoryRuntime"
                ),
            },
        }

    def _trim_undo_stack(self) -> None:
        overflow = (
            len(self._undo_stack)
            - self.maximum_history_size
        )

        if overflow > 0:
            del self._undo_stack[:overflow]

    def _emit(
        self,
        *,
        action: TimelineHistoryAction,
        command: TimelineHistoryCommand
        | None = None,
    ) -> TimelineHistoryEvent:
        state = self.state()

        event = TimelineHistoryEvent(
            action=action,
            production_id=(
                self.timeline.production_id
            ),
            command_id=(
                command.command_id
                if command
                else None
            ),
            operation_type=(
                command.operation_type
                if command
                else None
            ),
            undo_count=state.undo_count,
            redo_count=state.redo_count,
        )

        self._events.append(event)

        return event

    def _failure(
        self,
        message: str,
    ) -> TimelineHistoryResult:
        return TimelineHistoryResult(
            success=False,
            timeline=self.timeline,
            state=self.state(),
            error=message,
        )