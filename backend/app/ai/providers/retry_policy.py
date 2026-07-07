from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AIProviderRetryDecision:
    should_retry: bool
    reason: str
    next_max_tokens: int | None = None
    next_prompt_suffix: str | None = None


class AIProviderRetryPolicy:
    RETRYABLE_ERROR_KEYWORDS = [
        "timeout",
        "temporarily unavailable",
        "rate limit",
        "429",
        "500",
        "502",
        "503",
        "504",
        "server error",
        "connection",
    ]

    NON_RETRYABLE_ERROR_KEYWORDS = [
        "api key",
        "permission",
        "unauthorized",
        "forbidden",
        "invalid argument",
        "billing",
        "quota",
    ]

    def should_retry_exception(
        self,
        error: Exception,
        attempt: int,
        max_attempts: int,
    ) -> AIProviderRetryDecision:
        if attempt >= max_attempts:
            return AIProviderRetryDecision(False, "max_attempts_reached")

        message = str(error).lower()

        if any(keyword in message for keyword in self.NON_RETRYABLE_ERROR_KEYWORDS):
            return AIProviderRetryDecision(False, "non_retryable_error")

        if any(keyword in message for keyword in self.RETRYABLE_ERROR_KEYWORDS):
            return AIProviderRetryDecision(True, "retryable_provider_error")

        return AIProviderRetryDecision(False, "unknown_non_retryable_error")

    def should_retry_json_result(
        self,
        data: dict,
        raw_text: str,
        finish_reason: str,
        attempt: int,
        max_attempts: int,
        current_max_tokens: int | None,
    ) -> AIProviderRetryDecision:
        if attempt >= max_attempts:
            return AIProviderRetryDecision(False, "max_attempts_reached")

        if finish_reason.endswith("MAX_TOKENS") or finish_reason in {"length", "max_output_tokens"}:
            return AIProviderRetryDecision(
                True,
                "json_truncated_max_tokens",
                next_max_tokens=self._increase_max_tokens(current_max_tokens),
                next_prompt_suffix="\n\nReturn a complete valid JSON object. Do not truncate.",
            )

        if not data:
            return AIProviderRetryDecision(
                True,
                "json_parse_failed",
                next_prompt_suffix="\n\nReturn only valid JSON. No markdown. No explanation.",
            )

        return AIProviderRetryDecision(False, "json_valid")

    def _increase_max_tokens(self, current_max_tokens: int | None) -> int:
        if not current_max_tokens:
            return 2048

        return min(current_max_tokens * 2, 8192)