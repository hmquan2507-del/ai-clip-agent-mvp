from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.review.suggestions.lifecycle_models import (
    AISuggestionLifecycleSnapshot,
)


AI_SUGGESTION_APPLICATION_CONTRACT_VERSION = "16.6.3"


class ReviewAISuggestionOperation(str, Enum):
    GET = "get_suggestions"
    SELECT = "select_suggestion"
    APPLY = "apply_suggestion"
    DISMISS = "dismiss_suggestion"
    REGENERATE = "regenerate_suggestions"


def _clone_value(value: Any) -> Any:
    clone = getattr(value, "clone", None)
    if callable(clone):
        return clone()
    return deepcopy(value)


def _serialize_value(value: Any) -> Any:
    if value is None:
        return None
    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        return deepcopy(to_dict())
    return deepcopy(value)


@dataclass(frozen=True)
class ReviewAISuggestionApplicationResult:
    operation: ReviewAISuggestionOperation
    production_id: str
    session_id: str
    workspace_snapshot: Any
    suggestion_snapshot: AISuggestionLifecycleSnapshot
    timeline_command_result: Any | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        operation = self.operation
        if not isinstance(operation, ReviewAISuggestionOperation):
            operation = ReviewAISuggestionOperation(str(operation))

        production_id = str(self.production_id).strip()
        session_id = str(self.session_id).strip()
        if not production_id:
            raise ValueError("production_id is required.")
        if not session_id:
            raise ValueError("session_id is required.")
        if self.suggestion_snapshot.production_id != production_id:
            raise ValueError(
                "Suggestion snapshot production_id does not match."
            )

        workspace_production_id = getattr(
            self.workspace_snapshot,
            "production_id",
            production_id,
        )
        workspace_session_id = getattr(
            self.workspace_snapshot,
            "session_id",
            session_id,
        )
        if str(workspace_production_id) != production_id:
            raise ValueError(
                "Workspace snapshot production_id does not match."
            )
        if str(workspace_session_id) != session_id:
            raise ValueError(
                "Workspace snapshot session_id does not match."
            )

        object.__setattr__(self, "operation", operation)
        object.__setattr__(self, "production_id", production_id)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(
            self,
            "workspace_snapshot",
            _clone_value(self.workspace_snapshot),
        )
        object.__setattr__(
            self,
            "suggestion_snapshot",
            self.suggestion_snapshot.clone(),
        )
        object.__setattr__(
            self,
            "timeline_command_result",
            _clone_value(self.timeline_command_result),
        )
        object.__setattr__(self, "metadata", deepcopy(self.metadata))

    @property
    def timeline_revision(self) -> int:
        timeline = getattr(self.workspace_snapshot, "timeline", None)
        if timeline is not None:
            return int(timeline.revision)
        return int(self.suggestion_snapshot.timeline_revision)

    @property
    def lifecycle_revision(self) -> int:
        return self.suggestion_snapshot.lifecycle_revision

    def clone(self) -> ReviewAISuggestionApplicationResult:
        return deepcopy(self)

    def to_dict(self) -> dict[str, Any]:
        return deepcopy(
            {
                "contract_version": (
                    AI_SUGGESTION_APPLICATION_CONTRACT_VERSION
                ),
                "success": True,
                "operation": self.operation.value,
                "production_id": self.production_id,
                "session_id": self.session_id,
                "timeline_revision": self.timeline_revision,
                "lifecycle_revision": self.lifecycle_revision,
                "workspace_snapshot": _serialize_value(
                    self.workspace_snapshot
                ),
                "suggestion_snapshot": (
                    self.suggestion_snapshot.to_dict()
                ),
                "timeline_command_result": _serialize_value(
                    self.timeline_command_result
                ),
                "metadata": self.metadata,
            }
        )
