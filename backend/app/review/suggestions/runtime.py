from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from dataclasses import replace
from threading import RLock
from typing import Any

from app.review.suggestions.enums import (
    AISuggestionLifecycleEventType,
    AISuggestionStatus,
    AISuggestionStoreChangeReason,
)
from app.review.suggestions.lifecycle_models import (
    AISuggestionApplyPreparation,
    AISuggestionLifecycleEvent,
    AISuggestionLifecycleResult,
    AISuggestionLifecycleSnapshot,
)
from app.review.suggestions.models import (
    AISuggestion,
    AISuggestionReadModel,
)
from app.review.suggestions.store import (
    AISuggestionLifecycleStore,
)


AISuggestionLifecycleEventCallback = Callable[
    [AISuggestionLifecycleEvent],
    None,
]


class AISuggestionLifecycleRuntime:
    def __init__(
        self,
        store: AISuggestionLifecycleStore,
        *,
        event_callback: (
            AISuggestionLifecycleEventCallback
            | None
        ) = None,
        maximum_events: int = 100,
    ):
        if maximum_events < 1:
            raise ValueError(
                "maximum_events must be at least 1."
            )
        self.store = store
        self._event_callback = event_callback
        self._maximum_events = maximum_events
        self._events: list[
            AISuggestionLifecycleEvent
        ] = []
        self._lock = RLock()

    @property
    def production_id(self) -> str:
        return self.store.production_id

    @property
    def revision(self) -> int:
        return self.store.revision

    @property
    def events(
        self,
    ) -> list[AISuggestionLifecycleEvent]:
        with self._lock:
            return deepcopy(self._events)

    def snapshot(
        self,
    ) -> AISuggestionLifecycleSnapshot:
        return AISuggestionLifecycleSnapshot(
            production_id=self.production_id,
            lifecycle_revision=self.revision,
            read_model=self.store.snapshot(),
            metadata={
                "runtime": (
                    "AISuggestionLifecycleRuntime"
                ),
            },
        )

    def select(
        self,
        suggestion_id: str | None,
        *,
        expected_revision: int | None = None,
    ) -> AISuggestionLifecycleResult:
        with self._lock:
            try:
                self._assert_expected_revision(
                    expected_revision
                )
                current = self.store.snapshot()

                if (
                    suggestion_id is not None
                    and current.get(suggestion_id)
                    is None
                ):
                    return self._failure(
                        "AI suggestion was not found."
                    )

                if (
                    current.selected_suggestion_id
                    == suggestion_id
                ):
                    return self._success_without_event()

                next_model = replace(
                    current,
                    selected_suggestion_id=(
                        suggestion_id
                    ),
                )
                self.store.commit(
                    next_model,
                    reason=(
                        AISuggestionStoreChangeReason
                        .SELECT
                    ),
                    metadata={
                        "suggestion_id": (
                            suggestion_id
                        ),
                    },
                    expected_revision=(
                        expected_revision
                    ),
                )
                event = self._emit(
                    AISuggestionLifecycleEventType
                    .SUGGESTION_SELECTED,
                    suggestion_id=suggestion_id,
                )
                return self._success(event)
            except ValueError as exc:
                return self._failure(str(exc))

    def prepare_apply(
        self,
        suggestion_id: str,
        *,
        active_timeline_revision: int,
        expected_revision: int | None = None,
    ) -> AISuggestionApplyPreparation:
        with self._lock:
            try:
                self._assert_expected_revision(
                    expected_revision
                )
                suggestion = (
                    self._require_actionable(
                        suggestion_id,
                        active_timeline_revision,
                    )
                )
                return AISuggestionApplyPreparation(
                    success=True,
                    production_id=(
                        self.production_id
                    ),
                    lifecycle_revision=(
                        self.revision
                    ),
                    timeline_revision=(
                        active_timeline_revision
                    ),
                    suggestion=suggestion,
                    command=suggestion.command,
                )
            except ValueError as exc:
                current = self.store.snapshot()
                return AISuggestionApplyPreparation(
                    success=False,
                    production_id=(
                        self.production_id
                    ),
                    lifecycle_revision=(
                        self.revision
                    ),
                    timeline_revision=(
                        current.timeline_revision
                    ),
                    error=str(exc),
                )

    def mark_applied(
        self,
        suggestion_id: str,
        *,
        source_timeline_revision: int,
        resulting_timeline_revision: int,
        expected_revision: int | None = None,
    ) -> AISuggestionLifecycleResult:
        with self._lock:
            try:
                self._assert_expected_revision(
                    expected_revision
                )
                if (
                    resulting_timeline_revision
                    < source_timeline_revision
                ):
                    return self._failure(
                        "Resulting timeline revision "
                        "cannot move backwards."
                    )

                current = self.store.snapshot()
                suggestion = self._require_actionable(
                    suggestion_id,
                    source_timeline_revision,
                )
                updated: list[AISuggestion] = []

                for item in current.suggestions:
                    if (
                        item.suggestion_id
                        == suggestion.suggestion_id
                    ):
                        updated.append(
                            replace(
                                item,
                                status=(
                                    AISuggestionStatus
                                    .APPLIED
                                ),
                            )
                        )
                    elif (
                        item.status
                        == AISuggestionStatus.PROPOSED
                        and item.timeline_revision
                        != resulting_timeline_revision
                    ):
                        updated.append(
                            replace(
                                item,
                                status=(
                                    AISuggestionStatus
                                    .STALE
                                ),
                            )
                        )
                    else:
                        updated.append(item)

                next_model = replace(
                    current,
                    timeline_revision=(
                        resulting_timeline_revision
                    ),
                    suggestions=tuple(updated),
                    selected_suggestion_id=(
                        suggestion_id
                    ),
                )
                self.store.commit(
                    next_model,
                    reason=(
                        AISuggestionStoreChangeReason
                        .APPLY
                    ),
                    metadata={
                        "suggestion_id": suggestion_id,
                        "source_timeline_revision": (
                            source_timeline_revision
                        ),
                        "resulting_timeline_revision": (
                            resulting_timeline_revision
                        ),
                    },
                    expected_revision=(
                        expected_revision
                    ),
                )
                event = self._emit(
                    AISuggestionLifecycleEventType
                    .SUGGESTION_APPLIED,
                    suggestion_id=suggestion_id,
                    metadata={
                        "source_timeline_revision": (
                            source_timeline_revision
                        ),
                    },
                )
                return self._success(event)
            except ValueError as exc:
                return self._failure(str(exc))

    def dismiss(
        self,
        suggestion_id: str,
        *,
        expected_revision: int | None = None,
    ) -> AISuggestionLifecycleResult:
        with self._lock:
            try:
                self._assert_expected_revision(
                    expected_revision
                )
                current = self.store.snapshot()
                suggestion = current.get(
                    suggestion_id
                )
                if suggestion is None:
                    return self._failure(
                        "AI suggestion was not found."
                    )
                if (
                    suggestion.status
                    != AISuggestionStatus.PROPOSED
                ):
                    return self._failure(
                        "Only a proposed suggestion can "
                        "be dismissed."
                    )

                next_model = self._replace_status(
                    current,
                    suggestion_id,
                    AISuggestionStatus.DISMISSED,
                )
                self.store.commit(
                    next_model,
                    reason=(
                        AISuggestionStoreChangeReason
                        .DISMISS
                    ),
                    metadata={
                        "suggestion_id": suggestion_id,
                    },
                    expected_revision=(
                        expected_revision
                    ),
                )
                event = self._emit(
                    AISuggestionLifecycleEventType
                    .SUGGESTION_DISMISSED,
                    suggestion_id=suggestion_id,
                )
                return self._success(event)
            except ValueError as exc:
                return self._failure(str(exc))

    def regenerate(
        self,
        read_model: AISuggestionReadModel,
        *,
        expected_revision: int | None = None,
    ) -> AISuggestionLifecycleResult:
        with self._lock:
            try:
                self._assert_expected_revision(
                    expected_revision
                )
                if (
                    read_model.production_id
                    != self.production_id
                ):
                    return self._failure(
                        "Regenerated suggestions must use "
                        "the active production_id."
                    )
                self.store.commit(
                    read_model,
                    reason=(
                        AISuggestionStoreChangeReason
                        .REGENERATE
                    ),
                    metadata={
                        "suggestion_count": (
                            read_model.count
                        ),
                    },
                    expected_revision=(
                        expected_revision
                    ),
                )
                event = self._emit(
                    AISuggestionLifecycleEventType
                    .SUGGESTIONS_REGENERATED,
                    metadata={
                        "suggestion_count": (
                            read_model.count
                        ),
                    },
                )
                return self._success(event)
            except ValueError as exc:
                return self._failure(str(exc))

    def synchronize_timeline_revision(
        self,
        timeline_revision: int,
        *,
        expected_revision: int | None = None,
    ) -> AISuggestionLifecycleResult:
        with self._lock:
            try:
                self._assert_expected_revision(
                    expected_revision
                )
                if timeline_revision < 1:
                    return self._failure(
                        "timeline_revision must be at "
                        "least 1."
                    )
                current = self.store.snapshot()
                if (
                    current.timeline_revision
                    == timeline_revision
                ):
                    return self._success_without_event()

                suggestions = tuple(
                    replace(
                        item,
                        status=(
                            AISuggestionStatus.STALE
                        ),
                    )
                    if (
                        item.status
                        == AISuggestionStatus.PROPOSED
                        and item.timeline_revision
                        != timeline_revision
                    )
                    else item
                    for item in current.suggestions
                )
                next_model = replace(
                    current,
                    timeline_revision=timeline_revision,
                    suggestions=suggestions,
                )
                self.store.commit(
                    next_model,
                    reason=(
                        AISuggestionStoreChangeReason
                        .SYNCHRONIZE
                    ),
                    metadata={
                        "timeline_revision": (
                            timeline_revision
                        ),
                    },
                    expected_revision=(
                        expected_revision
                    ),
                )
                event = self._emit(
                    AISuggestionLifecycleEventType
                    .TIMELINE_SYNCHRONIZED,
                )
                return self._success(event)
            except ValueError as exc:
                return self._failure(str(exc))

    def reset(
        self,
        *,
        expected_revision: int | None = None,
    ) -> AISuggestionLifecycleResult:
        with self._lock:
            try:
                self.store.reset(
                    expected_revision=(
                        expected_revision
                    )
                )
                event = self._emit(
                    AISuggestionLifecycleEventType
                    .LIFECYCLE_RESET,
                )
                return self._success(event)
            except ValueError as exc:
                return self._failure(str(exc))

    def _require_actionable(
        self,
        suggestion_id: str,
        timeline_revision: int,
    ) -> AISuggestion:
        current = self.store.snapshot()
        suggestion = current.get(suggestion_id)
        if suggestion is None:
            raise ValueError(
                "AI suggestion was not found."
            )
        if not suggestion.actionable:
            raise ValueError(
                "AI suggestion is not actionable."
            )
        if (
            current.timeline_revision
            != timeline_revision
            or suggestion.timeline_revision
            != timeline_revision
        ):
            raise ValueError(
                "AI suggestion timeline revision is "
                "stale."
            )
        return suggestion

    @staticmethod
    def _replace_status(
        read_model: AISuggestionReadModel,
        suggestion_id: str,
        status: AISuggestionStatus,
    ) -> AISuggestionReadModel:
        return replace(
            read_model,
            suggestions=tuple(
                replace(item, status=status)
                if (
                    item.suggestion_id
                    == suggestion_id
                )
                else item
                for item in read_model.suggestions
            ),
        )

    def _assert_expected_revision(
        self,
        expected_revision: int | None,
    ) -> None:
        if (
            expected_revision is not None
            and expected_revision != self.revision
        ):
            raise ValueError(
                "AI suggestion lifecycle revision "
                "conflict: expected "
                f"{expected_revision}, current "
                f"{self.revision}."
            )

    def _emit(
        self,
        event_type: AISuggestionLifecycleEventType,
        *,
        suggestion_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AISuggestionLifecycleEvent:
        snapshot = self.snapshot()
        event = AISuggestionLifecycleEvent(
            event_type=event_type,
            production_id=self.production_id,
            lifecycle_revision=(
                snapshot.lifecycle_revision
            ),
            timeline_revision=(
                snapshot.timeline_revision
            ),
            suggestion_id=suggestion_id,
            metadata=deepcopy(metadata or {}),
        )
        self._events.append(event.clone())
        if (
            len(self._events)
            > self._maximum_events
        ):
            self._events = self._events[
                -self._maximum_events:
            ]

        if self._event_callback is not None:
            try:
                self._event_callback(event.clone())
            except Exception:
                pass
        return event.clone()

    def _success(
        self,
        event: AISuggestionLifecycleEvent,
    ) -> AISuggestionLifecycleResult:
        return AISuggestionLifecycleResult(
            success=True,
            snapshot=self.snapshot(),
            event=event,
        )

    def _success_without_event(
        self,
    ) -> AISuggestionLifecycleResult:
        return AISuggestionLifecycleResult(
            success=True,
            snapshot=self.snapshot(),
        )

    def _failure(
        self,
        error: str,
    ) -> AISuggestionLifecycleResult:
        return AISuggestionLifecycleResult(
            success=False,
            snapshot=self.snapshot(),
            error=error,
        )
