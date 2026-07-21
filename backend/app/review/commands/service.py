from __future__ import annotations

from app.review.commands.errors import (
    AICommandRevisionConflictError,
    AICommandSubmissionError,
)
from app.review.commands.models import (
    AICommandSubmission,
    AICommandSubmissionResult,
)
from app.review.commands.store import (
    AICommandSubmissionStore,
)


class AICommandSubmissionService:
    def __init__(self, *, workspace_service, store):
        self.workspace_service = workspace_service
        self.store: AICommandSubmissionStore = store
        self._operation_lock = getattr(
            workspace_service,
            "operation_lock",
            None,
        )

    def submit(
        self,
        production_id: str,
        *,
        session_id: str,
        command_text: str,
        expected_timeline_revision: int | None = None,
        client_request_id: str | None = None,
    ) -> AICommandSubmissionResult:
        lock = self._operation_lock
        if lock is None:
            raise AICommandSubmissionError(
                "Workspace operation lock is unavailable.",
                production_id=production_id,
                session_id=session_id,
            )
        with lock:
            session = self.workspace_service.get_session(
                production_id,
                session_id=session_id,
            )
            before = session.snapshot()
            revision = int(before.timeline.revision)
            if (
                expected_timeline_revision is not None
                and int(expected_timeline_revision) != revision
            ):
                raise AICommandRevisionConflictError(
                    "Timeline revision does not match expected revision.",
                    production_id=production_id,
                    session_id=session_id,
                    expected_revision=int(
                        expected_timeline_revision
                    ),
                    current_revision=revision,
                )
            submission = AICommandSubmission(
                production_id=production_id,
                session_id=session_id,
                command_text=command_text,
                timeline_revision=revision,
                client_request_id=client_request_id,
                metadata={
                    "execution_authorized": False,
                    "proposal_created": False,
                },
            )
            stored, duplicate = self.store.add(submission)
            after = session.snapshot()
            if after.timeline.to_dict() != before.timeline.to_dict():
                raise AICommandSubmissionError(
                    "Command submission changed timeline state.",
                    production_id=production_id,
                    session_id=session_id,
                )
            return AICommandSubmissionResult(
                submission=stored,
                duplicate=duplicate,
            )
