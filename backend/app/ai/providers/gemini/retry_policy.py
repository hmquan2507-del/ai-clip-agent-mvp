from __future__ import annotations

from dataclasses import dataclass

from app.ai.providers.retry_policy import (
    AIProviderRetryDecision as GeminiRetryDecision,
    AIProviderRetryPolicy as GeminiRetryPolicy,
)

__all__ = [
    "GeminiRetryDecision",
    "GeminiRetryPolicy",
]

@dataclass
class GeminiRetryDecision:
    should_retry: bool
    reason: str
    next_max_tokens: int | None = None
    next_prompt_suffix: str | None = None


class GeminiRetryPolicy:
    RETRYABLE_ERROR_KEYWORDS = [
        "timeout",
        "temporarily unavailable",
        "rate limit",
        "429",
        "500",
        "502",
        "503",
        "504",
    ]

    NON_RETRYABLE_ERROR_KEYWORDS = [
        "api key",
        "permission",
        "unauthorized",
        "forbidden",
        "invalid argument",
        "billing",
    ]

    def should_retry_exception(
        self,
        error: Exception,
        attempt: int,
        max_attempts: int,
    ) -> GeminiRetryDecision:
        if attempt >= max_attempts:
            return GeminiRetryDecision(
                should_retry=False,
                reason="max_attempts_reached",
            )

        message = str(error).lower()

        if any(keyword in message for keyword in self.NON_RETRYABLE_ERROR_KEYWORDS):
            return GeminiRetryDecision(
                should_retry=False,
                reason="non_retryable_error",
            )

        if any(keyword in message for keyword in self.RETRYABLE_ERROR_KEYWORDS):
            return GeminiRetryDecision(
                should_retry=True,
                reason="retryable_provider_error",
            )

        return GeminiRetryDecision(
            should_retry=False,
            reason="unknown_non_retryable_error",
        )

    def should_retry_json_result(
        self,
        data: dict,
        raw_text: str,
        finish_reason: str,
        attempt: int,
        max_attempts: int,
        current_max_tokens: int | None,
    ) -> GeminiRetryDecision:
        if attempt >= max_attempts:
            return GeminiRetryDecision(
                should_retry=False,
                reason="max_attempts_reached",
            )

        if finish_reason.endswith("MAX_TOKENS"):
            return GeminiRetryDecision(
                should_retry=True,
                reason="json_truncated_max_tokens",
                next_max_tokens=self._increase_max_tokens(current_max_tokens),
                next_prompt_suffix=(
                    "\n\nReturn a complete valid JSON object. "
                    "Do not truncate the response."
                ),
            )

        if not data:
            return GeminiRetryDecision(
                should_retry=True,
                reason="json_parse_failed",
                next_prompt_suffix=(
                    "\n\nReturn only valid JSON. "
                    "Do not include markdown, comments, or explanation."
                ),
            )

        return GeminiRetryDecision(
            should_retry=False,
            reason="json_valid",
        )

    def _increase_max_tokens(
        self,
        current_max_tokens: int | None,
    ) -> int:
        if not current_max_tokens:
            return 2048

        return min(current_max_tokens * 2, 8192)