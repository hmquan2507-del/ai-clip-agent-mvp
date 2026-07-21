from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.review.application.errors import (
    ReviewRuntimeSessionConflictError,
    ReviewRuntimeSessionOperationError,
)


class ReviewAISuggestionOperationError(
    ReviewRuntimeSessionOperationError
):
    code = "review_ai_suggestion_operation_failed"

    def __init__(
        self,
        message: str,
        *,
        production_id: str,
        session_id: str,
        operation: str,
        suggestion_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        super().__init__(
            message,
            production_id=production_id,
            session_id=session_id,
        )
        self.operation = str(operation).strip()
        self.suggestion_id = (
            str(suggestion_id).strip()
            if suggestion_id is not None
            else None
        )
        self.metadata = deepcopy(metadata or {})

    def to_dict(self) -> dict[str, Any]:
        payload = super().to_dict()
        payload.update(
            {
                "operation": self.operation,
                "suggestion_id": self.suggestion_id,
                "metadata": deepcopy(self.metadata),
            }
        )
        return payload


class ReviewAISuggestionRevisionConflictError(
    ReviewRuntimeSessionConflictError
):
    code = "review_ai_suggestion_revision_conflict"

    def __init__(
        self,
        message: str,
        *,
        production_id: str,
        session_id: str,
        expected_revision: int,
        current_revision: int,
    ):
        super().__init__(
            message,
            production_id=production_id,
            session_id=session_id,
        )
        self.expected_revision = int(expected_revision)
        self.current_revision = int(current_revision)

    def to_dict(self) -> dict[str, Any]:
        payload = super().to_dict()
        payload.update(
            {
                "expected_revision": self.expected_revision,
                "current_revision": self.current_revision,
            }
        )
        return payload
