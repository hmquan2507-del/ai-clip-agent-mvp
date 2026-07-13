from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.review.editing.clipboard.runtime import (
    TimelineClipboardRuntime,
)
from app.review.editing.history.runtime import (
    TimelineCommandHistoryRuntime,
)
from app.review.editing.runtime import (
    TimelineMutationRuntime,
)
from app.review.editing.state.store import (
    TimelineRuntimeStore,
)
from app.review.models import ReviewWorkspace
from app.review.preview.runtime import (
    PreviewSessionRuntime,
)
from app.review.selection.runtime import (
    TimelineSelectionRuntime,
)


@dataclass(frozen=True)
class ReviewRuntimeGraph:
    workspace: ReviewWorkspace

    preview_runtime: PreviewSessionRuntime
    selection_runtime: TimelineSelectionRuntime

    timeline_store: TimelineRuntimeStore
    mutation_runtime: TimelineMutationRuntime
    history_runtime: TimelineCommandHistoryRuntime
    clipboard_runtime: TimelineClipboardRuntime

    @property
    def production_id(self) -> str:
        return self.workspace.production_id

    @property
    def component_production_ids(
        self,
    ) -> tuple[str, ...]:
        return (
            self.workspace.production_id,
            self.preview_runtime.source.production_id,
            self.selection_runtime.catalog.production_id,
            self.timeline_store.production_id,
            self.mutation_runtime.store.production_id,
            self.history_runtime.store.production_id,
            self.clipboard_runtime.store.production_id,
        )

    @property
    def production_ids_match(self) -> bool:
        return (
            len(
                set(
                    self.component_production_ids
                )
            )
            == 1
        )

    @property
    def shared_store(self) -> bool:
        return (
            self.mutation_runtime.store
            is self.timeline_store
            and self.history_runtime.store
            is self.timeline_store
            and self.clipboard_runtime.store
            is self.timeline_store
        )

    def validate(self) -> None:
        if not self.production_ids_match:
            raise ValueError(
                "Review runtime graph components "
                "must use the same production_id."
            )

        if not self.shared_store:
            raise ValueError(
                "Mutation, history and clipboard "
                "runtimes must share one timeline store."
            )

    def to_dict(self) -> dict[str, Any]:
        timeline = self.timeline_store.snapshot()

        return {
            "production_id": self.production_id,
            "production_ids_match": (
                self.production_ids_match
            ),
            "shared_store": self.shared_store,
            "timeline_revision": (
                timeline.revision
            ),
            "timeline_dirty": timeline.dirty,
            "track_count": timeline.track_count,
            "clip_count": timeline.clip_count,
            "preview_available": (
                self.preview_runtime
                .source.available
            ),
            "selection_track_count": len(
                self.selection_runtime
                .catalog.tracks
            ),
            "selection_clip_count": len(
                self.selection_runtime
                .catalog.clips
            ),
            "history": (
                self.history_runtime
                .state().to_dict()
            ),
            "clipboard": (
                self.clipboard_runtime
                .state().to_dict()
            ),
            "components": {
                "preview": type(
                    self.preview_runtime
                ).__name__,
                "selection": type(
                    self.selection_runtime
                ).__name__,
                "timeline_store": type(
                    self.timeline_store
                ).__name__,
                "mutation": type(
                    self.mutation_runtime
                ).__name__,
                "history": type(
                    self.history_runtime
                ).__name__,
                "clipboard": type(
                    self.clipboard_runtime
                ).__name__,
            },
        }