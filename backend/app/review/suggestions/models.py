from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from math import isfinite
from typing import Any

from app.review.suggestions.enums import (
    AISuggestionKind,
    AISuggestionStatus,
    AISuggestionTargetType,
)


AI_SUGGESTION_CONTRACT_VERSION = "16.6.1"


def utc_now_iso() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


@dataclass(frozen=True)
class AISuggestionTarget:
    production_id: str
    target_type: AISuggestionTargetType

    track_id: str | None = None
    clip_id: str | None = None
    start_time: float | None = None
    end_time: float | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "production_id",
            _require_identifier(
                self.production_id,
                "production_id",
            ),
        )

        for field_name in (
            "track_id",
            "clip_id",
        ):
            value = getattr(self, field_name)
            if value is not None:
                object.__setattr__(
                    self,
                    field_name,
                    _require_identifier(
                        value,
                        field_name,
                    ),
                )

        for field_name in (
            "start_time",
            "end_time",
        ):
            value = getattr(self, field_name)
            if (
                value is not None
                and not isfinite(value)
            ):
                raise ValueError(
                    f"{field_name} must be finite."
                )

        if (
            self.target_type
            == AISuggestionTargetType.TRACK
            and not self.track_id
        ):
            raise ValueError(
                "Track suggestion target requires "
                "track_id."
            )

        if (
            self.target_type
            == AISuggestionTargetType.CLIP
            and not self.clip_id
        ):
            raise ValueError(
                "Clip suggestion target requires "
                "clip_id."
            )

        if (
            self.target_type
            == AISuggestionTargetType.RANGE
        ):
            if (
                self.start_time is None
                or self.end_time is None
                or self.start_time < 0
                or self.end_time
                <= self.start_time
            ):
                raise ValueError(
                    "Range suggestion target requires "
                    "a valid start_time and end_time."
                )

        object.__setattr__(
            self,
            "metadata",
            deepcopy(self.metadata),
        )

    def clone(self) -> AISuggestionTarget:
        return deepcopy(self)

    def to_dict(self) -> dict[str, Any]:
        return deepcopy(
            {
                "production_id": self.production_id,
                "target_type": self.target_type.value,
                "track_id": self.track_id,
                "clip_id": self.clip_id,
                "start_time": self.start_time,
                "end_time": self.end_time,
                "metadata": self.metadata,
            }
        )


@dataclass(frozen=True)
class AISuggestionCommandProposal:
    operation: str
    arguments: dict[str, Any] = field(
        default_factory=dict
    )
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "operation",
            _require_identifier(
                self.operation,
                "operation",
            ),
        )
        object.__setattr__(
            self,
            "arguments",
            deepcopy(self.arguments),
        )
        object.__setattr__(
            self,
            "metadata",
            deepcopy(self.metadata),
        )

    def clone(
        self,
    ) -> AISuggestionCommandProposal:
        return deepcopy(self)

    def to_dict(self) -> dict[str, Any]:
        return deepcopy(
            {
                "operation": self.operation,
                "arguments": self.arguments,
                "metadata": self.metadata,
            }
        )


@dataclass(frozen=True)
class AISuggestion:
    suggestion_id: str
    production_id: str
    kind: AISuggestionKind
    status: AISuggestionStatus
    title: str
    description: str
    timeline_revision: int
    target: AISuggestionTarget

    command: (
        AISuggestionCommandProposal | None
    ) = None
    score: float | None = None
    created_at: str = field(
        default_factory=utc_now_iso
    )
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "suggestion_id",
            _require_identifier(
                self.suggestion_id,
                "suggestion_id",
            ),
        )
        object.__setattr__(
            self,
            "production_id",
            _require_identifier(
                self.production_id,
                "production_id",
            ),
        )
        object.__setattr__(
            self,
            "title",
            _require_text(self.title, "title"),
        )
        object.__setattr__(
            self,
            "description",
            _require_text(
                self.description,
                "description",
            ),
        )

        if self.timeline_revision < 1:
            raise ValueError(
                "timeline_revision must be at "
                "least 1."
            )

        if (
            self.target.production_id
            != self.production_id
        ):
            raise ValueError(
                "Suggestion and target must use "
                "the same production_id."
            )

        if (
            self.score is not None
            and not 0 <= self.score <= 100
        ):
            raise ValueError(
                "score must be between 0 and 100."
            )

        object.__setattr__(
            self,
            "metadata",
            deepcopy(self.metadata),
        )

    @property
    def actionable(self) -> bool:
        return (
            self.status
            == AISuggestionStatus.PROPOSED
            and self.command is not None
        )

    @property
    def stale(self) -> bool:
        return (
            self.status
            == AISuggestionStatus.STALE
        )

    def clone(self) -> AISuggestion:
        return deepcopy(self)

    def to_dict(self) -> dict[str, Any]:
        return deepcopy(
            {
                "contract_version": (
                    AI_SUGGESTION_CONTRACT_VERSION
                ),
                "suggestion_id": self.suggestion_id,
                "production_id": self.production_id,
                "kind": self.kind.value,
                "status": self.status.value,
                "title": self.title,
                "description": self.description,
                "timeline_revision": (
                    self.timeline_revision
                ),
                "target": self.target.to_dict(),
                "command": (
                    self.command.to_dict()
                    if self.command
                    else None
                ),
                "score": self.score,
                "actionable": self.actionable,
                "stale": self.stale,
                "created_at": self.created_at,
                "metadata": self.metadata,
            }
        )


@dataclass(frozen=True)
class AISuggestionReadModel:
    production_id: str
    timeline_revision: int
    suggestions: tuple[AISuggestion, ...] = ()

    selected_suggestion_id: str | None = None
    generated_at: str = field(
        default_factory=utc_now_iso
    )
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "production_id",
            _require_identifier(
                self.production_id,
                "production_id",
            ),
        )

        if self.timeline_revision < 1:
            raise ValueError(
                "timeline_revision must be at "
                "least 1."
            )

        suggestions = tuple(
            suggestion.clone()
            for suggestion in self.suggestions
        )
        object.__setattr__(
            self,
            "suggestions",
            suggestions,
        )
        object.__setattr__(
            self,
            "metadata",
            deepcopy(self.metadata),
        )

        suggestion_ids = [
            item.suggestion_id
            for item in suggestions
        ]

        if (
            len(suggestion_ids)
            != len(set(suggestion_ids))
        ):
            raise ValueError(
                "Suggestion IDs must be unique."
            )

        if any(
            item.production_id
            != self.production_id
            for item in suggestions
        ):
            raise ValueError(
                "All suggestions must use the read "
                "model production_id."
            )

        if (
            self.selected_suggestion_id
            is not None
            and self.selected_suggestion_id
            not in suggestion_ids
        ):
            raise ValueError(
                "selected_suggestion_id must exist "
                "in suggestions."
            )

    @property
    def count(self) -> int:
        return len(self.suggestions)

    @property
    def actionable_count(self) -> int:
        return sum(
            1
            for item in self.suggestions
            if item.actionable
        )

    @property
    def stale_count(self) -> int:
        return sum(
            1
            for item in self.suggestions
            if item.stale
        )

    def get(
        self,
        suggestion_id: str,
    ) -> AISuggestion | None:
        for suggestion in self.suggestions:
            if (
                suggestion.suggestion_id
                == suggestion_id
            ):
                return suggestion.clone()
        return None

    def clone(self) -> AISuggestionReadModel:
        return deepcopy(self)

    def to_dict(self) -> dict[str, Any]:
        return deepcopy(
            {
                "contract_version": (
                    AI_SUGGESTION_CONTRACT_VERSION
                ),
                "production_id": self.production_id,
                "timeline_revision": (
                    self.timeline_revision
                ),
                "suggestions": [
                    item.to_dict()
                    for item in self.suggestions
                ],
                "selected_suggestion_id": (
                    self.selected_suggestion_id
                ),
                "count": self.count,
                "actionable_count": (
                    self.actionable_count
                ),
                "stale_count": self.stale_count,
                "generated_at": self.generated_at,
                "metadata": self.metadata,
            }
        )


def _require_identifier(
    value: str,
    name: str,
) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(
            f"{name} must not be empty."
        )
    return normalized


def _require_text(
    value: str,
    name: str,
) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(
            f"{name} must not be empty."
        )
    return normalized
