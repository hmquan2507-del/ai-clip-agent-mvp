from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable

from app.ai.providers.gemini.retry_policy import GeminiRetryPolicy

from app.ai.providers.retry_runtime import (
    AIProviderRetryResult as GeminiRetryResult,
    AIProviderRetryRuntime as GeminiRetryRuntime,
)

__all__ = [
    "GeminiRetryResult",
    "GeminiRetryRuntime",
]
@dataclass
class GeminiRetryResult:
    value: Any
    attempts: int
    retried: bool
    retry_reasons: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class GeminiRetryRuntime:
    def __init__(
        self,
        policy: GeminiRetryPolicy | None = None,
        max_attempts: int = 3,
        sleep_seconds: float = 0.5,
    ):
        self.policy = policy or GeminiRetryPolicy()
        self.max_attempts = max_attempts
        self.sleep_seconds = sleep_seconds

    def run_call(
        self,
        call: Callable[[], Any],
    ) -> GeminiRetryResult:
        retry_reasons: list[str] = []

        for attempt in range(1, self.max_attempts + 1):
            try:
                value = call()

                return GeminiRetryResult(
                    value=value,
                    attempts=attempt,
                    retried=attempt > 1,
                    retry_reasons=retry_reasons,
                    metadata={
                        "mode": "exception_retry",
                    },
                )

            except Exception as error:
                decision = self.policy.should_retry_exception(
                    error=error,
                    attempt=attempt,
                    max_attempts=self.max_attempts,
                )

                retry_reasons.append(decision.reason)

                if not decision.should_retry:
                    raise

                time.sleep(self.sleep_seconds * attempt)

        raise RuntimeError("Gemini retry runtime exhausted unexpectedly")