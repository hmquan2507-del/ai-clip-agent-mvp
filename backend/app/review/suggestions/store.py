from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from threading import RLock
from typing import Any

from app.review.suggestions.enums import (
    AISuggestionStoreChangeReason,
)
from app.review.suggestions.lifecycle_models import (
    AISuggestionStoreChange,
)
from app.review.suggestions.models import (
    AISuggestionReadModel,
    utc_now_iso,
)


AISuggestionStoreSubscriber = Callable[
    [AISuggestionStoreChange],
    None,
]


class AISuggestionLifecycleStore:
    def __init__(
        self,
        read_model: AISuggestionReadModel,
        *,
        maximum_changes: int = 100,
    ):
        if maximum_changes < 1:
            raise ValueError(
                "maximum_changes must be at least 1."
            )
        self._initial = read_model.clone()
        self._active = read_model.clone()
        self._revision = 1
        self._maximum_changes = maximum_changes
        self._changes: list[
            AISuggestionStoreChange
        ] = []
        self._subscribers: set[
            AISuggestionStoreSubscriber
        ] = set()
        self._lock = RLock()

    @property
    def production_id(self) -> str:
        return self._active.production_id

    @property
    def revision(self) -> int:
        with self._lock:
            return self._revision

    @property
    def changes(
        self,
    ) -> list[AISuggestionStoreChange]:
        with self._lock:
            return deepcopy(self._changes)

    def snapshot(self) -> AISuggestionReadModel:
        with self._lock:
            return self._active.clone()

    def commit(
        self,
        read_model: AISuggestionReadModel,
        *,
        reason: AISuggestionStoreChangeReason,
        metadata: dict[str, Any] | None = None,
        expected_revision: int | None = None,
    ) -> AISuggestionStoreChange:
        callbacks: tuple[
            AISuggestionStoreSubscriber,
            ...,
        ]
        with self._lock:
            self._assert_expected_revision(
                expected_revision
            )
            self._assert_production_id(
                read_model
            )

            before = self._active.clone()
            after = read_model.clone()
            next_revision = self._revision + 1
            change = AISuggestionStoreChange(
                reason=reason,
                production_id=self.production_id,
                lifecycle_revision=(
                    next_revision
                ),
                before=before,
                after=after,
                metadata=deepcopy(
                    metadata or {}
                ),
            )

            self._active = after
            self._revision = next_revision
            self._changes.append(change.clone())
            if (
                len(self._changes)
                > self._maximum_changes
            ):
                self._changes = self._changes[
                    -self._maximum_changes:
                ]
            callbacks = tuple(
                self._subscribers
            )

        for callback in callbacks:
            try:
                callback(change.clone())
            except Exception:
                continue

        return change.clone()

    def replace(
        self,
        read_model: AISuggestionReadModel,
        *,
        metadata: dict[str, Any] | None = None,
        expected_revision: int | None = None,
    ) -> AISuggestionStoreChange:
        return self.commit(
            read_model,
            reason=(
                AISuggestionStoreChangeReason.REPLACE
            ),
            metadata=metadata,
            expected_revision=expected_revision,
        )

    def reset(
        self,
        *,
        expected_revision: int | None = None,
    ) -> AISuggestionStoreChange:
        return self.commit(
            self._initial,
            reason=(
                AISuggestionStoreChangeReason.RESET
            ),
            metadata={
                "reset_to_initial": True,
                "reset_at": utc_now_iso(),
            },
            expected_revision=expected_revision,
        )

    def subscribe(
        self,
        callback: AISuggestionStoreSubscriber,
    ) -> None:
        with self._lock:
            self._subscribers.add(callback)

    def unsubscribe(
        self,
        callback: AISuggestionStoreSubscriber,
    ) -> None:
        with self._lock:
            self._subscribers.discard(callback)

    def _assert_expected_revision(
        self,
        expected_revision: int | None,
    ) -> None:
        if (
            expected_revision is not None
            and expected_revision != self._revision
        ):
            raise ValueError(
                "AI suggestion lifecycle revision "
                "conflict: expected "
                f"{expected_revision}, current "
                f"{self._revision}."
            )

    def _assert_production_id(
        self,
        read_model: AISuggestionReadModel,
    ) -> None:
        if (
            read_model.production_id
            != self.production_id
        ):
            raise ValueError(
                "AI suggestion store cannot accept "
                "a different production_id."
            )
