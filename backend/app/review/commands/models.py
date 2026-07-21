from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


AI_COMMAND_SUBMISSION_CONTRACT_VERSION = "16.6.8"


class AICommandSubmissionStatus(str, Enum):
    ACCEPTED = "accepted"


@dataclass(frozen=True)
class AICommandSubmission:
    production_id: str
    session_id: str
    command_text: str
    timeline_revision: int
    submission_id: str = field(
        default_factory=lambda: str(uuid4())
    )
    status: AICommandSubmissionStatus = (
        AICommandSubmissionStatus.ACCEPTED
    )
    client_request_id: str | None = None
    created_at: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        production_id = str(self.production_id).strip()
        session_id = str(self.session_id).strip()
        command_text = " ".join(
            str(self.command_text).split()
        )
        if not production_id:
            raise ValueError("production_id is required.")
        if not session_id:
            raise ValueError("session_id is required.")
        if not command_text:
            raise ValueError("command_text is required.")
        if len(command_text) > 2000:
            raise ValueError(
                "command_text must contain at most 2000 characters."
            )
        if int(self.timeline_revision) < 1:
            raise ValueError("timeline_revision must be positive.")
        object.__setattr__(self, "production_id", production_id)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "command_text", command_text)
        object.__setattr__(
            self,
            "timeline_revision",
            int(self.timeline_revision),
        )
        object.__setattr__(self, "metadata", deepcopy(self.metadata))

    def clone(self) -> AICommandSubmission:
        return deepcopy(self)

    def to_dict(self) -> dict[str, Any]:
        return deepcopy(
            {
                "contract_version": (
                    AI_COMMAND_SUBMISSION_CONTRACT_VERSION
                ),
                "submission_id": self.submission_id,
                "production_id": self.production_id,
                "session_id": self.session_id,
                "command_text": self.command_text,
                "timeline_revision": self.timeline_revision,
                "status": self.status.value,
                "client_request_id": self.client_request_id,
                "created_at": self.created_at,
                "metadata": self.metadata,
            }
        )


@dataclass(frozen=True)
class AICommandSubmissionResult:
    submission: AICommandSubmission
    duplicate: bool = False

    def clone(self) -> AICommandSubmissionResult:
        return deepcopy(self)

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_version": AI_COMMAND_SUBMISSION_CONTRACT_VERSION,
            "success": True,
            "operation": "submit_command",
            "production_id": self.submission.production_id,
            "session_id": self.submission.session_id,
            "timeline_revision": self.submission.timeline_revision,
            "submission": self.submission.to_dict(),
            "duplicate": self.duplicate,
            "timeline_mutated": False,
        }
