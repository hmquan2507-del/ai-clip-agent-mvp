from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.render.execution.recovery.enums import (
    RenderCleanupMode,
    RenderFailureCategory,
    RenderRetryDecision,
)


@dataclass
class RenderFailureClassification:
    category: RenderFailureCategory | str
    retry_decision: RenderRetryDecision | str
    cleanup_mode: RenderCleanupMode | str

    reason: str
    retry_delay_seconds: float = 0.0

    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self._value(self.category),
            "retry_decision": self._value(
                self.retry_decision
            ),
            "cleanup_mode": self._value(
                self.cleanup_mode
            ),
            "reason": self.reason,
            "retry_delay_seconds": (
                self.retry_delay_seconds
            ),
            "metadata": self.metadata,
        }

    def _value(self, value: Any) -> str:
        return (
            value.value
            if hasattr(value, "value")
            else str(value)
        )


@dataclass
class RenderRetryPolicy:
    max_attempts: int = 3
    base_delay_seconds: float = 1.0
    backoff_multiplier: float = 2.0
    max_delay_seconds: float = 30.0

    retry_timeout: bool = True
    retry_process_error: bool = True
    retry_output_missing: bool = True
    retry_output_invalid: bool = False
    retry_disk_full: bool = False

    def delay_for_attempt(
        self,
        attempt_number: int,
    ) -> float:
        exponent = max(0, attempt_number - 1)

        delay = (
            self.base_delay_seconds
            * (self.backoff_multiplier ** exponent)
        )

        return min(
            self.max_delay_seconds,
            delay,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_attempts": self.max_attempts,
            "base_delay_seconds": (
                self.base_delay_seconds
            ),
            "backoff_multiplier": (
                self.backoff_multiplier
            ),
            "max_delay_seconds": (
                self.max_delay_seconds
            ),
            "retry_timeout": self.retry_timeout,
            "retry_process_error": (
                self.retry_process_error
            ),
            "retry_output_missing": (
                self.retry_output_missing
            ),
            "retry_output_invalid": (
                self.retry_output_invalid
            ),
            "retry_disk_full": (
                self.retry_disk_full
            ),
        }


@dataclass
class RenderRetryAttempt:
    attempt_number: int
    started_at: str
    finished_at: str

    success: bool
    duration_seconds: float

    category: str | None = None
    retry_decision: str | None = None
    error: str | None = None

    output_path: str | None = None
    cleanup_paths: list[str] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "attempt_number": self.attempt_number,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "success": self.success,
            "duration_seconds": self.duration_seconds,
            "category": self.category,
            "retry_decision": self.retry_decision,
            "error": self.error,
            "output_path": self.output_path,
            "cleanup_paths": list(
                self.cleanup_paths
            ),
            "metadata": self.metadata,
        }


@dataclass
class RenderCleanupResult:
    success: bool
    removed_paths: list[str]
    preserved_paths: list[str]
    issues: list[str]
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "removed_paths": list(
                self.removed_paths
            ),
            "preserved_paths": list(
                self.preserved_paths
            ),
            "issues": list(self.issues),
            "metadata": self.metadata,
        }


@dataclass
class RenderRecoveryResult:
    production_id: str
    success: bool

    attempt_count: int
    attempts: list[RenderRetryAttempt]

    final_output_path: str | None = None
    final_error: str | None = None

    diagnostics_path: str | None = None
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "success": self.success,
            "attempt_count": self.attempt_count,
            "attempts": [
                item.to_dict()
                for item in self.attempts
            ],
            "final_output_path": (
                self.final_output_path
            ),
            "final_error": self.final_error,
            "diagnostics_path": (
                self.diagnostics_path
            ),
            "metadata": self.metadata,
        }