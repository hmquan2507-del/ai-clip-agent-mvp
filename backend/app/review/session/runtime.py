from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from copy import deepcopy
from dataclasses import replace
from typing import Any

from app.review.editing.models import (
    EditableTimeline,
)
from app.review.editing.state.models import (
    TimelineStateChange,
)
from app.review.models import (
    ReviewWorkspace,
    SelectionState,
    TimelineState,
)
from app.review.selection.factory import (
    build_selection_catalog,
)
from app.review.session.enums import (
    PreviewTimelineSyncStatus,
    ReviewRuntimeSessionEventType,
    ReviewRuntimeSessionStatus,
)
from app.review.session.graph import (
    ReviewRuntimeGraph,
)
from app.review.session.models import (
    PreviewTimelineSyncState,
    ReviewRuntimeSessionEvent,
    ReviewRuntimeSessionResult,
    ReviewRuntimeSessionSnapshot,
    ReviewRuntimeSessionState,
    utc_now_iso,
)


ReviewRuntimeSessionEventCallback = Callable[
    [ReviewRuntimeSessionEvent],
    None,
]


class ReviewRuntimeSession:
    def __init__(
        self,
        graph: ReviewRuntimeGraph,
        *,
        event_callback: (
            ReviewRuntimeSessionEventCallback
            | None
        ) = None,
    ):
        graph.validate()

        self.graph = graph
        self.event_callback = event_callback

        timeline = (
            self.graph.timeline_store.snapshot()
        )

        initial_state = (
            ReviewRuntimeSessionState.create(
                production_id=(
                    graph.production_id
                ),
                timeline_revision=(
                    timeline.revision
                ),
                dirty=timeline.dirty,
                metadata={
                    "runtime": (
                        "ReviewRuntimeSession"
                    ),
                },
            )
        )

        self._state = replace(
            initial_state,
            status=(
                ReviewRuntimeSessionStatus.READY
            ),
            updated_at=utc_now_iso(),
        )

        self._preview_timeline_revision = (
            timeline.revision
        )
        self._preview_timeline_signature = (
            self._timeline_signature(timeline)
        )

        self._preview_sync = (
            self._build_preview_sync(
                timeline,
                reason="session_created",
            )
        )

        self._events: list[
            ReviewRuntimeSessionEvent
        ] = []

        self.graph.timeline_store.subscribe(
            self._handle_timeline_change
        )

        self._emit(
            ReviewRuntimeSessionEventType
            .SESSION_CREATED,
            metadata={
                "shared_store": (
                    self.graph.shared_store
                ),
            },
        )

        self._emit(
            ReviewRuntimeSessionEventType
            .SESSION_READY,
            metadata={
                "preview_sync_status": (
                    self._preview_sync
                    .status.value
                ),
            },
        )

    @property
    def production_id(self) -> str:
        return self._state.production_id

    @property
    def session_id(self) -> str:
        return self._state.session_id

    @property
    def state(
        self,
    ) -> ReviewRuntimeSessionState:
        return deepcopy(self._state)

    @property
    def preview_sync(
        self,
    ) -> PreviewTimelineSyncState:
        return deepcopy(
            self._preview_sync
        )

    @property
    def events(
        self,
    ) -> list[ReviewRuntimeSessionEvent]:
        return deepcopy(self._events)

    @property
    def closed(self) -> bool:
        return self._state.closed

    def close(
        self,
    ) -> ReviewRuntimeSessionResult:
        if self.closed:
            return ReviewRuntimeSessionResult(
                success=True,
                state=self.state,
            )

        self.graph.timeline_store.unsubscribe(
            self._handle_timeline_change
        )

        now = utc_now_iso()

        self._state = replace(
            self._state,
            status=(
                ReviewRuntimeSessionStatus.CLOSED
            ),
            revision=(
                self._state.revision + 1
            ),
            updated_at=now,
            closed_at=now,
            error=None,
        )

        event = self._emit(
            ReviewRuntimeSessionEventType
            .SESSION_CLOSED,
        )

        return ReviewRuntimeSessionResult(
            success=True,
            state=self.state,
            event=event,
        )

    def snapshot(
        self,
    ) -> ReviewRuntimeSessionSnapshot:
        timeline = (
            self.graph.timeline_store.snapshot()
        )

        selection_state = (
            self.graph.selection_runtime.state
        )

        workspace = self._build_workspace_view(
            timeline,
            selected_clip_ids=(
                selection_state
                .selected_clip_ids
            ),
        )

        snapshot = ReviewRuntimeSessionSnapshot(
            session=self.state,
            workspace=workspace,
            timeline=timeline,
            preview_source=deepcopy(
                self.graph.preview_runtime.source
            ),
            preview_state=(
                self.graph.preview_runtime.state
            ),
            preview_sync=self.preview_sync,
            selection_catalog=deepcopy(
                self.graph.selection_runtime
                .catalog
            ),
            selection_state=selection_state,
            history_state=(
                self.graph.history_runtime.state()
            ),
            clipboard_state=(
                self.graph.clipboard_runtime.state()
            ),
            clipboard_content=(
                self.graph.clipboard_runtime.content
            ),
            metadata={
                "contract_version": "16.1.7.4",
                "runtime": (
                    "ReviewRuntimeSession"
                ),
            },
        )

        return snapshot.clone()

    def select_clip(
        self,
        clip_id: str,
        *,
        additive: bool = False,
        move_cursor: bool = False,
    ) -> ReviewRuntimeSessionResult:
        if self.closed:
            return ReviewRuntimeSessionResult(
                success=False,
                state=self.state,
                error=(
                    "Closed review runtime session "
                    "cannot change selection."
                ),
            )

        selection_result = (
            self.graph.selection_runtime
            .select_clip(
                clip_id,
                additive=additive,
                move_cursor=move_cursor,
            )
        )

        if not selection_result.success:
            return ReviewRuntimeSessionResult(
                success=False,
                state=self.state,
                error=(
                    selection_result.error
                    or (
                        "Timeline clip selection "
                        "failed."
                    )
                ),
            )

        timeline = (
            self.graph.timeline_store.snapshot()
        )

        selection_state = (
            self.graph.selection_runtime.state
        )

        self._state = replace(
            self._state,
            status=(
                ReviewRuntimeSessionStatus.READY
            ),
            timeline_revision=(
                timeline.revision
            ),
            dirty=timeline.dirty,
            revision=(
                self._state.revision + 1
            ),
            updated_at=utc_now_iso(),
            error=None,
        )

        event = self._emit(
            ReviewRuntimeSessionEventType
            .SELECTION_CHANGED,
            metadata={
                "clip_id": clip_id,
                "additive": additive,
                "cursor_moved": move_cursor,
                "selection_revision": (
                    selection_state.revision
                ),
                "selection_event_type": (
                    selection_result.event
                    .event_type.value
                    if selection_result.event
                    else None
                ),
                "selected_clip_ids": list(
                    selection_state
                    .selected_clip_ids
                ),
                "selected_track_ids": list(
                    selection_state
                    .selected_track_ids
                ),
                "active_clip_id": (
                    selection_state
                    .active_clip_id
                ),
                "active_track_id": (
                    selection_state
                    .active_track_id
                ),
                "cursor_time": (
                    selection_state.cursor_time
                ),
                "cursor_frame": (
                    selection_state.cursor_frame
                ),
            },
        )

        return ReviewRuntimeSessionResult(
            success=True,
            state=self.state,
            snapshot=self.snapshot(),
            event=event,
        )

    def reset(
        self,
    ) -> ReviewRuntimeSessionResult:
        if self.closed:
            return ReviewRuntimeSessionResult(
                success=False,
                state=self.state,
                error=(
                    "Closed review runtime session "
                    "cannot be reset."
                ),
            )

        history_result = (
            self.graph.history_runtime.reset()
        )

        if not history_result.success:
            return ReviewRuntimeSessionResult(
                success=False,
                state=self.state,
                error=(
                    history_result.error
                    or (
                        "Timeline history reset "
                        "failed."
                    )
                ),
            )

        preview_result = (
            self.graph.preview_runtime.reset()
        )
        selection_result = (
            self.graph.selection_runtime.reset()
        )
        clipboard_result = (
            self.graph.clipboard_runtime.clear()
        )
        clipboard_history_result = (
            self.graph.clipboard_runtime
            .clear_history()
        )

        component_errors = [
            result.error
            for result in (
                preview_result,
                selection_result,
                clipboard_result,
                clipboard_history_result,
            )
            if not result.success
            and result.error
        ]

        if component_errors:
            message = "; ".join(
                component_errors
            )
            self._set_error(message)

            return ReviewRuntimeSessionResult(
                success=False,
                state=self.state,
                error=message,
            )

        timeline = (
            self.graph.timeline_store.snapshot()
        )

        self._preview_sync = (
            self._build_preview_sync(
                timeline,
                reason="session_reset",
            )
        )

        self._state = replace(
            self._state,
            status=(
                ReviewRuntimeSessionStatus.READY
            ),
            timeline_revision=(
                timeline.revision
            ),
            dirty=timeline.dirty,
            revision=(
                self._state.revision + 1
            ),
            updated_at=utc_now_iso(),
            error=None,
        )

        event = self._emit(
            ReviewRuntimeSessionEventType
            .SESSION_RESET,
            metadata={
                "timeline_revision": (
                    timeline.revision
                ),
                "preview_reset": True,
                "selection_reset": True,
                "clipboard_reset": True,
                "history_reset": True,
            },
        )

        return ReviewRuntimeSessionResult(
            success=True,
            state=self.state,
            snapshot=self.snapshot(),
            event=event,
        )

    def clear_events(self) -> None:
        self._events.clear()

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": self.state.to_dict(),
            "preview_sync": (
                self.preview_sync.to_dict()
            ),
            "selection": (
                self.graph.selection_runtime
                .to_dict()
            ),
            "event_count": len(
                self._events
            ),
            "events": [
                event.to_dict()
                for event in self.events
            ],
        }

    def _handle_timeline_change(
        self,
        change: TimelineStateChange,
    ) -> None:
        if self.closed:
            return

        try:
            timeline = (
                self.graph.timeline_store
                .snapshot()
            )

            catalog = build_selection_catalog(
                production_id=(
                    timeline.production_id
                ),
                duration=timeline.duration,
                tracks=timeline.tracks,
                fps=timeline.fps,
            )

            selection_result = (
                self.graph.selection_runtime
                .synchronize_catalog(catalog)
            )

            if not selection_result.success:
                self._set_error(
                    selection_result.error
                    or (
                        "Selection synchronization "
                        "failed."
                    )
                )
                return

            self._preview_sync = (
                self._build_preview_sync(
                    timeline,
                    reason=change.reason,
                )
            )

            self._state = replace(
                self._state,
                status=(
                    ReviewRuntimeSessionStatus
                    .READY
                ),
                timeline_revision=(
                    timeline.revision
                ),
                dirty=timeline.dirty,
                revision=(
                    self._state.revision + 1
                ),
                updated_at=utc_now_iso(),
                error=None,
            )

            self._emit(
                ReviewRuntimeSessionEventType
                .TIMELINE_CHANGED,
                metadata={
                    "change": change.to_dict(),
                    "selection_synchronized": (
                        True
                    ),
                    "selection_event_type": (
                        selection_result.event
                        .event_type.value
                        if selection_result.event
                        else None
                    ),
                    "preview_sync_status": (
                        self._preview_sync
                        .status.value
                    ),
                },
            )

        except Exception as error:
            self._set_error(str(error))

    def _build_workspace_view(
        self,
        timeline: EditableTimeline,
        *,
        selected_clip_ids: list[str],
    ) -> ReviewWorkspace:
        source_workspace = deepcopy(
            self.graph.workspace
        )

        timeline_state = TimelineState(
            version=timeline.version,
            duration=timeline.duration,
            track_count=timeline.track_count,
            clip_count=timeline.clip_count,
            tracks=[
                track.to_dict()
                for track in timeline.tracks
            ],
        )

        selection_state = SelectionState(
            selected_clip_ids=list(
                selected_clip_ids
            ),
        )

        metadata = deepcopy(
            source_workspace.metadata
        )

        metadata["runtime_session"] = {
            "session_id": self.session_id,
            "session_revision": (
                self._state.revision
            ),
            "timeline_revision": (
                timeline.revision
            ),
            "timeline_dirty": timeline.dirty,
        }

        return replace(
            source_workspace,
            timeline=timeline_state,
            selection=selection_state,
            metadata=metadata,
        )

    def _build_preview_sync(
        self,
        timeline: EditableTimeline,
        *,
        reason: str,
    ) -> PreviewTimelineSyncState:
        if not (
            self.graph.preview_runtime
            .source.available
        ):
            status = (
                PreviewTimelineSyncStatus
                .UNAVAILABLE
            )
            signature_matches = False
        else:
            signature_matches = (
                self._timeline_signature(
                    timeline
                )
                == self._preview_timeline_signature
            )

            status = (
                PreviewTimelineSyncStatus.CURRENT
                if signature_matches
                else PreviewTimelineSyncStatus
                .STALE
            )

        return PreviewTimelineSyncState(
            production_id=(
                timeline.production_id
            ),
            status=status,
            active_timeline_revision=(
                timeline.revision
            ),
            preview_timeline_revision=(
                self._preview_timeline_revision
                if self.graph.preview_runtime
                .source.available
                else None
            ),
            reason=reason,
            metadata={
                "signature_matches": (
                    signature_matches
                ),
            },
        )

    def _set_error(
        self,
        message: str,
    ) -> None:
        timeline = (
            self.graph.timeline_store.snapshot()
        )

        self._state = replace(
            self._state,
            status=(
                ReviewRuntimeSessionStatus.ERROR
            ),
            timeline_revision=(
                timeline.revision
            ),
            dirty=timeline.dirty,
            revision=(
                self._state.revision + 1
            ),
            updated_at=utc_now_iso(),
            error=message,
        )

        self._emit(
            ReviewRuntimeSessionEventType
            .SESSION_ERROR,
            metadata={
                "error": message,
            },
        )

    def _emit(
        self,
        event_type: ReviewRuntimeSessionEventType,
        *,
        metadata: dict[str, Any]
        | None = None,
    ) -> ReviewRuntimeSessionEvent:
        event = ReviewRuntimeSessionEvent(
            event_type=event_type,
            session_id=self.session_id,
            production_id=self.production_id,
            session_revision=(
                self._state.revision
            ),
            timeline_revision=(
                self._state.timeline_revision
            ),
            metadata=deepcopy(
                metadata or {}
            ),
        )

        self._events.append(event)

        if self.event_callback:
            self.event_callback(
                deepcopy(event)
            )

        return deepcopy(event)

    def _timeline_signature(
        self,
        timeline: EditableTimeline,
    ) -> str:
        payload = timeline.to_dict()

        for key in (
            "revision",
            "dirty",
            "dirty_status",
            "created_at",
            "updated_at",
        ):
            payload.pop(key, None)

        serialized = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            default=str,
        )

        return hashlib.sha256(
            serialized.encode("utf-8")
        ).hexdigest()