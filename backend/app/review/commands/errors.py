from __future__ import annotations

from app.review.application.errors import (
    ReviewRuntimeSessionConflictError,
    ReviewRuntimeSessionOperationError,
)


class AICommandSubmissionError(
    ReviewRuntimeSessionOperationError
):
    code = "review_ai_command_submission_failed"


class AICommandRevisionConflictError(
    ReviewRuntimeSessionConflictError
):
    code = "review_ai_command_revision_conflict"

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

    def to_dict(self):
        payload = super().to_dict()
        payload.update(
            {
                "expected_revision": self.expected_revision,
                "current_revision": self.current_revision,
            }
        )
        return payload
