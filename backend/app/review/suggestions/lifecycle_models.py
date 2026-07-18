from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from app.review.suggestions.enums import (
    AISuggestionLifecycleEventType,
    AISuggestionStoreChangeReason,
)
from app.review.suggestions.models import (
    AI_SUGGESTION_CONTRACT_VERSION,
    AISuggestion,
    AISuggestionCommandProposal,
    AISuggestionReadModel,
    utc_now_iso,
)


@dataclass(frozen=True)
class AISuggestionLifecycleSnapshot:
    production_id: str
    lifecycle_revision: int
    read_model: AISuggestionReadModel
    created_at: str = field(
        default_factory=utc_now_iso
    )
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if self.lifecycle_revision < 1:
            raise ValueError(
                "lifecycle_revision must be at "
                "least 1."
            )
        if (
            self.read_model.production_id
            != self.production_id
        ):
            raise ValueError(
                "Lifecycle snapshot and read model "
                "must use the same production_id."
            )
        object.__setattr__(
            self,
            "read_model",
            self.read_model.clone(),
        )
        object.__setattr__(
            self,
            "metadata",
            deepcopy(self.metadata),
        )

    @property
    def timeline_revision(self) -> int:
        return self.read_model.timeline_revision

    def clone(
        self,
    ) -> AISuggestionLifecycleSnapshot:
        return deepcopy(self)

    def to_dict(self) -> dict[str, Any]:
        return deepcopy(
            {
                "contract_version": (
                    AI_SUGGESTION_CONTRACT_VERSION
                ),
                "production_id": self.production_id,
                "lifecycle_revision": (
                    self.lifecycle_revision
                ),
                "timeline_revision": (
                    self.timeline_revision
                ),
                "read_model": (
                    self.read_model.to_dict()
                ),
                "created_at": self.created_at,
                "metadata": self.metadata,
            }
        )


@dataclass(frozen=True)
class AISuggestionStoreChange:
    reason: AISuggestionStoreChangeReason
    production_id: str
    lifecycle_revision: int
    before: AISuggestionReadModel
    after: AISuggestionReadModel
    created_at: str = field(
        default_factory=utc_now_iso
    )
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if self.lifecycle_revision < 2:
            raise ValueError(
                "Store change lifecycle_revision "
                "must be at least 2."
            )
        if (
            self.before.production_id
            != self.production_id
            or self.after.production_id
            != self.production_id
        ):
            raise ValueError(
                "Suggestion store change production "
                "IDs must match."
            )
        object.__setattr__(
            self,
            "before",
            self.before.clone(),
        )
        object.__setattr__(
            self,
            "after",
            self.after.clone(),
        )
        object.__setattr__(
            self,
            "metadata",
            deepcopy(self.metadata),
        )

    def clone(self) -> AISuggestionStoreChange:
        return deepcopy(self)

    def to_dict(self) -> dict[str, Any]:
        return deepcopy(
            {
                "reason": self.reason.value,
                "production_id": self.production_id,
                "lifecycle_revision": (
                    self.lifecycle_revision
                ),
                "before": self.before.to_dict(),
                "after": self.after.to_dict(),
                "created_at": self.created_at,
                "metadata": self.metadata,
            }
        )


@dataclass(frozen=True)
class AISuggestionLifecycleEvent:
    event_type: AISuggestionLifecycleEventType
    production_id: str
    lifecycle_revision: int
    timeline_revision: int
    suggestion_id: str | None = None
    event_id: str = field(
        default_factory=lambda: str(uuid4())
    )
    created_at: str = field(
        default_factory=utc_now_iso
    )
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if self.lifecycle_revision < 1:
            raise ValueError(
                "lifecycle_revision must be at "
                "least 1."
            )
        if self.timeline_revision < 1:
            raise ValueError(
                "timeline_revision must be at "
                "least 1."
            )
        object.__setattr__(
            self,
            "metadata",
            deepcopy(self.metadata),
        )

    def clone(self) -> AISuggestionLifecycleEvent:
        return deepcopy(self)

    def to_dict(self) -> dict[str, Any]:
        return deepcopy(
            {
                "event_id": self.event_id,
                "event_type": self.event_type.value,
                "production_id": self.production_id,
                "lifecycle_revision": (
                    self.lifecycle_revision
                ),
                "timeline_revision": (
                    self.timeline_revision
                ),
                "suggestion_id": self.suggestion_id,
                "created_at": self.created_at,
                "metadata": self.metadata,
            }
        )


@dataclass(frozen=True)
class AISuggestionLifecycleResult:
    success: bool
    snapshot: AISuggestionLifecycleSnapshot
    event: AISuggestionLifecycleEvent | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return deepcopy(
            {
                "success": self.success,
                "snapshot": self.snapshot.to_dict(),
                "event": (
                    self.event.to_dict()
                    if self.event
                    else None
                ),
                "error": self.error,
            }
        )


@dataclass(frozen=True)
class AISuggestionApplyPreparation:
    success: bool
    production_id: str
    lifecycle_revision: int
    timeline_revision: int
    suggestion: AISuggestion | None = None
    command: (
        AISuggestionCommandProposal | None
    ) = None
    error: str | None = None

    def __post_init__(self) -> None:
        if self.suggestion is not None:
            object.__setattr__(
                self,
                "suggestion",
                self.suggestion.clone(),
            )
        if self.command is not None:
            object.__setattr__(
                self,
                "command",
                self.command.clone(),
            )

    def to_dict(self) -> dict[str, Any]:
        return deepcopy(
            {
                "success": self.success,
                "production_id": self.production_id,
                "lifecycle_revision": (
                    self.lifecycle_revision
                ),
                "timeline_revision": (
                    self.timeline_revision
                ),
                "suggestion": (
                    self.suggestion.to_dict()
                    if self.suggestion
                    else None
                ),
                "command": (
                    self.command.to_dict()
                    if self.command
                    else None
                ),
                "error": self.error,
            }
        )
