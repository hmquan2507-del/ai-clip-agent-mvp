from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable

from app.ai.providers.retry_policy import AIProviderRetryPolicy


@dataclass
class AIProviderRetryResult:
    value: Any
    attempts: int
    retried: bool
    retry_reasons: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class AIProviderRetryRuntime:
    def __init__(
        self,
        policy: AIProviderRetryPolicy | None = None,
        max_attempts: int = 3,
        sleep_seconds: float = 0.5,
    ):
        self.policy = policy or AIProviderRetryPolicy()
        self.max_attempts = max_attempts
        self.sleep_seconds = sleep_seconds

    def run_call(
        self,
        call: Callable[[], Any],
    ) -> AIProviderRetryResult:
        retry_reasons: list[str] = []

        for attempt in range(1, self.max_attempts + 1):
            try:
                value = call()

                return AIProviderRetryResult(
                    value=value,
                    attempts=attempt,
                    retried=attempt > 1,
                    retry_reasons=retry_reasons,
                    metadata={"mode": "provider_exception_retry"},
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

        raise RuntimeError("AI provider retry runtime exhausted unexpectedly")