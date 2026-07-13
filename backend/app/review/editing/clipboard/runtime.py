from __future__ import annotations

from copy import deepcopy
from typing import Any
from uuid import uuid4

from app.review.editing.clipboard.enums import (
    TimelineClipboardAction,
    TimelineClipboardEventType,
    TimelineClipboardItemType,
    TimelineClipboardStatus,
)
from app.review.editing.clipboard.models import (
    TimelineClipboardContent,
    TimelineClipboardEvent,
    TimelineClipboardHistoryEntry,
    TimelineClipboardHistoryState,
    TimelineClipboardItem,
    TimelineClipboardResult,
    TimelineClipboardState,
)
from app.review.editing.enums import TimelineEditingOperationType
from app.review.editing.history.models import TimelineHistoryResult
from app.review.editing.history.runtime import TimelineCommandHistoryRuntime
from app.review.editing.models import EditableTimeline, EditableTimelineClip
from app.review.editing.state.store import TimelineRuntimeStore


class TimelineClipboardRuntime:
    def __init__(
        self,
        timeline: EditableTimeline | None = None,
        *,
        store: TimelineRuntimeStore | None = None,
        history_runtime: TimelineCommandHistoryRuntime | None = None,
        maximum_history_size: int = 20,
    ):
        if history_runtime is not None:
            history_store = history_runtime.store

            if store is not None and store is not history_store:
                raise ValueError(
                    "Clipboard and history must use the same runtime store."
                )

            if (
                timeline is not None
                and timeline.production_id != history_store.production_id
            ):
                raise ValueError(
                    "Clipboard timeline production_id does not match "
                    "history runtime store."
                )

            resolved_store = history_store
        else:
            if timeline is None and store is None:
                raise ValueError("Timeline or runtime store is required.")

            if timeline is not None and store is not None:
                raise ValueError(
                    "Provide either timeline or runtime store, not both."
                )

            resolved_store = store or TimelineRuntimeStore(timeline=timeline)

        self.store = resolved_store
        self.history_runtime = history_runtime
        self.maximum_history_size = max(1, int(maximum_history_size))

        self._content = TimelineClipboardContent.empty(
            self.store.production_id
        )
        self._events: list[TimelineClipboardEvent] = []
        self._history: list[TimelineClipboardHistoryEntry] = []

    @property
    def timeline(self) -> EditableTimeline:
        return self.store.snapshot()

    @property
    def content(self) -> TimelineClipboardContent:
        return deepcopy(self._content)

    @property
    def events(self) -> list[TimelineClipboardEvent]:
        return deepcopy(self._events)

    @property
    def history_entries(self) -> list[TimelineClipboardHistoryEntry]:
        return deepcopy(self._history)

    @property
    def has_content(self) -> bool:
        return self._content.available

    def snapshot(self) -> EditableTimeline:
        return self.store.snapshot()

    def state(self) -> TimelineClipboardState:
        return TimelineClipboardState(
            production_id=self.store.production_id,
            status=self._content.status,
            available=self._content.available,
            item_count=self._content.item_count,
            clip_count=self._content.clip_count,
            clipboard_id=self._content.clipboard_id,
            last_action=(
                self._content.action if self._content.available else None
            ),
            source_track_ids=self._content.source_track_ids,
        )

    def history_state(self) -> TimelineClipboardHistoryState:
        return TimelineClipboardHistoryState(
            entry_count=len(self._history),
            maximum_history_size=self.maximum_history_size,
            latest_entry_id=(
                self._history[-1].entry_id if self._history else None
            ),
        )

    def copy_clip(self, clip_id: str) -> TimelineClipboardResult:
        return self.copy_clips([clip_id])

    def copy_clips(self, clip_ids: list[str]) -> TimelineClipboardResult:
        return self._copy_clips(
            clip_ids=clip_ids,
            action=TimelineClipboardAction.COPY,
            save_history=True,
        )

    def cut_clip(self, clip_id: str) -> TimelineClipboardResult:
        return self.cut_clips([clip_id])

    def cut_clips(self, clip_ids: list[str]) -> TimelineClipboardResult:
        if self.history_runtime is None:
            return self._failure(
                "Cut Runtime cần Timeline Command History Runtime.",
                event_type=TimelineClipboardEventType.CUT_FAILED,
            )

        previous_content = deepcopy(self._content)
        copy_result = self._copy_clips(
            clip_ids=clip_ids,
            action=TimelineClipboardAction.CUT,
            save_history=False,
        )

        if not copy_result.success:
            return copy_result

        history_result = self.history_runtime.execute(
            operation_type=TimelineEditingOperationType.CUT_CLIPS,
            label="Cắt clip",
            mutation=lambda: (
                self.history_runtime.mutation_runtime.delete_clips(clip_ids)
            ),
            metadata={"clip_ids": list(clip_ids)},
        )

        if not history_result.success:
            self._content = previous_content
            return self._failure(
                history_result.error or "Không thể cắt clip.",
                event_type=TimelineClipboardEventType.CUT_FAILED,
                timeline_history_result=history_result,
            )

        self._append_history(self._content)

        event_type = (
            TimelineClipboardEventType.CLIP_CUT
            if self._content.item_count == 1
            else TimelineClipboardEventType.CLIPS_CUT
        )
        event = self._emit(
            event_type=event_type,
            metadata={
                "clip_ids": [
                    item.source_clip_id for item in self._content.items
                ]
            },
        )

        return self._success(
            event=event,
            timeline_history_result=history_result,
        )

    def paste(
        self,
        *,
        at_time: float,
        target_track_id: str | None = None,
        track_mapping: dict[str, str] | None = None,
    ) -> TimelineClipboardResult:
        if not self._content.available:
            return self._failure(
                "Clipboard đang trống.",
                event_type=TimelineClipboardEventType.PASTE_FAILED,
            )

        if self.history_runtime is None:
            return self._failure(
                "Paste Runtime cần Timeline Command History Runtime.",
                event_type=TimelineClipboardEventType.PASTE_FAILED,
            )

        paste_time = max(0.0, float(at_time))
        source_tracks = self._content.source_track_ids

        if (
            target_track_id is not None
            and len(source_tracks) > 1
            and not track_mapping
        ):
            return self._failure(
                "Không thể dán nhiều source track vào một track nếu "
                "chưa cung cấp track_mapping.",
                event_type=TimelineClipboardEventType.PASTE_FAILED,
            )

        resolved_mapping = dict(track_mapping or {})
        if target_track_id is not None and len(source_tracks) == 1:
            resolved_mapping[source_tracks[0]] = target_track_id

        paste_group_id = uuid4().hex[:8]
        clips_to_insert: list[EditableTimelineClip] = []

        for index, item in enumerate(self._content.items):
            clip = item.clone_clip()
            clip.clip_id = (
                f"{item.source_clip_id}_paste_{paste_group_id}_{index}"
            )
            clip.track_id = resolved_mapping.get(
                item.source_track_id,
                item.source_track_id,
            )
            clip.start_time = paste_time + item.relative_start
            clip.end_time = paste_time + item.relative_end
            clip.metadata = {
                **clip.metadata,
                "clipboard_id": self._content.clipboard_id,
                "clipboard_source_clip_id": item.source_clip_id,
                "paste_group_id": paste_group_id,
            }
            clips_to_insert.append(clip)

        history_result = self.history_runtime.execute(
            operation_type=TimelineEditingOperationType.PASTE_CLIPS,
            label="Dán clip",
            mutation=lambda: (
                self.history_runtime.mutation_runtime.insert_clips(
                    clips_to_insert
                )
            ),
            metadata={
                "clipboard_id": self._content.clipboard_id,
                "paste_time": paste_time,
                "paste_group_id": paste_group_id,
                "clip_count": len(clips_to_insert),
            },
        )

        if not history_result.success:
            return self._failure(
                history_result.error or "Không thể dán clip.",
                event_type=TimelineClipboardEventType.PASTE_FAILED,
                timeline_history_result=history_result,
            )

        event_type = (
            TimelineClipboardEventType.CLIP_PASTED
            if len(clips_to_insert) == 1
            else TimelineClipboardEventType.CLIPS_PASTED
        )
        event = self._emit(
            event_type=event_type,
            metadata={
                "paste_time": paste_time,
                "paste_group_id": paste_group_id,
                "pasted_clip_ids": [
                    clip.clip_id for clip in clips_to_insert
                ],
                "track_mapping": resolved_mapping,
            },
        )

        return self._success(
            event=event,
            timeline_history_result=history_result,
        )

    def restore_history_entry(
        self,
        entry_id: str,
    ) -> TimelineClipboardResult:
        entry = next(
            (item for item in self._history if item.entry_id == entry_id),
            None,
        )

        if entry is None:
            return self._failure(
                "Không tìm thấy clipboard history entry.",
                event_type=TimelineClipboardEventType.COPY_FAILED,
            )

        self._content = deepcopy(entry.content)
        event = self._emit(
            event_type=TimelineClipboardEventType.HISTORY_RESTORED,
            metadata={"entry_id": entry_id},
        )
        return self._success(event=event)

    def clear_history(self) -> TimelineClipboardResult:
        self._history.clear()
        event = self._emit(
            event_type=TimelineClipboardEventType.HISTORY_CLEARED
        )
        return self._success(event=event)

    def clear(self) -> TimelineClipboardResult:
        previous_id = self._content.clipboard_id
        self._content = TimelineClipboardContent.empty(
            self.store.production_id
        )
        event = self._emit(
            event_type=TimelineClipboardEventType.CLIPBOARD_CLEARED,
            metadata={"previous_clipboard_id": previous_id},
        )
        return self._success(event=event)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timeline": self.store.snapshot().to_dict(),
            "content": self._content.to_dict(),
            "state": self.state().to_dict(),
            "history_state": self.history_state().to_dict(),
            "history": [item.to_dict() for item in self._history],
            "events": [event.to_dict() for event in self._events],
            "metadata": {
                "runtime": "TimelineClipboardRuntime",
                "store_revision": self.store.revision,
                "history_enabled": self.history_runtime is not None,
            },
        }

    def _copy_clips(
        self,
        *,
        clip_ids: list[str],
        action: TimelineClipboardAction,
        save_history: bool,
    ) -> TimelineClipboardResult:
        normalized_ids = list(
            dict.fromkeys(
                str(item).strip()
                for item in clip_ids
                if str(item).strip()
            )
        )

        if not normalized_ids:
            return self._failure(
                "Không có clip nào được chọn.",
                event_type=TimelineClipboardEventType.COPY_FAILED,
            )

        current_timeline = self.store.snapshot()
        clips: list[EditableTimelineClip] = []
        missing_ids: list[str] = []

        for clip_id in normalized_ids:
            clip = current_timeline.get_clip(clip_id)
            if clip is None:
                missing_ids.append(clip_id)
            else:
                clips.append(clip.clone())

        if missing_ids:
            return self._failure(
                "Không tìm thấy clip: " + ", ".join(missing_ids),
                event_type=TimelineClipboardEventType.COPY_FAILED,
            )

        clips.sort(
            key=lambda item: (
                item.start_time,
                self._track_position(current_timeline, item.track_id),
                item.clip_id,
            )
        )

        anchor_time = min(clip.start_time for clip in clips)
        maximum_end = max(clip.end_time for clip in clips)
        items = tuple(
            TimelineClipboardItem(
                item_id=str(uuid4()),
                item_type=TimelineClipboardItemType.CLIP,
                source_clip_id=clip.clip_id,
                source_track_id=clip.track_id,
                clip=clip.clone(),
                relative_start=clip.start_time - anchor_time,
                relative_end=clip.end_time - anchor_time,
                source_order=index,
            )
            for index, clip in enumerate(clips)
        )

        self._content = TimelineClipboardContent(
            clipboard_id=str(uuid4()),
            production_id=current_timeline.production_id,
            action=action,
            status=TimelineClipboardStatus.READY,
            items=items,
            anchor_time=anchor_time,
            total_duration=maximum_end - anchor_time,
        )

        if save_history:
            self._append_history(self._content)

        event_type = (
            TimelineClipboardEventType.CLIP_COPIED
            if len(items) == 1
            else TimelineClipboardEventType.CLIPS_COPIED
        )
        event = self._emit(event_type=event_type)
        return self._success(event=event)

    def _append_history(self, content: TimelineClipboardContent) -> None:
        self._history.append(
            TimelineClipboardHistoryEntry.create(deepcopy(content))
        )

        overflow = len(self._history) - self.maximum_history_size
        if overflow > 0:
            del self._history[:overflow]

    def _track_position(
        self,
        timeline: EditableTimeline,
        track_id: str,
    ) -> int:
        track = timeline.get_track(track_id)
        return track.position if track else 0

    def _emit(
        self,
        *,
        event_type: TimelineClipboardEventType,
        metadata: dict[str, Any] | None = None,
    ) -> TimelineClipboardEvent:
        event = TimelineClipboardEvent(
            event_type=event_type,
            production_id=self.store.production_id,
            clipboard_id=self._content.clipboard_id,
            item_count=self._content.item_count,
            metadata=dict(metadata or {}),
        )
        self._events.append(event)
        return deepcopy(event)

    def _success(
        self,
        *,
        event: TimelineClipboardEvent | None = None,
        timeline_history_result: TimelineHistoryResult | None = None,
    ) -> TimelineClipboardResult:
        return TimelineClipboardResult(
            success=True,
            content=deepcopy(self._content),
            state=self.state(),
            event=deepcopy(event),
            timeline_history_result=deepcopy(timeline_history_result),
        )

    def _failure(
        self,
        message: str,
        *,
        event_type: TimelineClipboardEventType,
        timeline_history_result: TimelineHistoryResult | None = None,
    ) -> TimelineClipboardResult:
        event = self._emit(
            event_type=event_type,
            metadata={"error": message},
        )
        return TimelineClipboardResult(
            success=False,
            content=deepcopy(self._content),
            state=self.state(),
            event=event,
            error=message,
            timeline_history_result=deepcopy(timeline_history_result),
        )