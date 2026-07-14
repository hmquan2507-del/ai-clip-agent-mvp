from __future__ import annotations

from copy import deepcopy
from typing import Any


class ReviewWorkspaceApplicationError(RuntimeError):
    code = "review_application_error"

    def __init__(
        self,
        message: str,
        *,
        production_id: str | None = None,
        session_id: str | None = None,
    ):
        super().__init__(message)
        self.production_id = production_id
        self.session_id = session_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": str(self),
            "production_id": self.production_id,
            "session_id": self.session_id,
        }


class ReviewRuntimeSessionNotFoundError(
    ReviewWorkspaceApplicationError
):
    code = "review_session_not_found"


class ReviewRuntimeSessionConflictError(
    ReviewWorkspaceApplicationError
):
    code = "review_session_conflict"


class ReviewRuntimeSessionOperationError(
    ReviewWorkspaceApplicationError
):
    code = "review_session_operation_failed"


class ReviewTimelineRevisionConflictError(
    ReviewRuntimeSessionConflictError
):
    code = "review_timeline_revision_conflict"

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

        self.expected_revision = int(
            expected_revision
        )
        self.current_revision = int(
            current_revision
        )

    def to_dict(self) -> dict[str, Any]:
        payload = super().to_dict()
        payload.update(
            {
                "expected_revision": (
                    self.expected_revision
                ),
                "current_revision": (
                    self.current_revision
                ),
            }
        )
        return payload


class ReviewTimelineCommandOperationError(
    ReviewRuntimeSessionOperationError
):
    code = "review_timeline_command_failed"

    def __init__(
        self,
        message: str,
        *,
        production_id: str,
        session_id: str,
        operation: str,
        metadata: dict[str, Any] | None = None,
    ):
        super().__init__(
            message,
            production_id=production_id,
            session_id=session_id,
        )

        self.operation = str(
            operation
        ).strip()
        self.metadata = deepcopy(
            metadata or {}
        )

    def to_dict(self) -> dict[str, Any]:
        payload = super().to_dict()
        payload.update(
            {
                "operation": self.operation,
                "metadata": deepcopy(
                    self.metadata
                ),
            }
        )
        return payload