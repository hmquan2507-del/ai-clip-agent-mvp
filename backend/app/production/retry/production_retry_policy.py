from __future__ import annotations

from dataclasses import dataclass

from app.production.contracts import PipelineResult, PipelineStatus


@dataclass
class ProductionRetryDecision:
    should_retry: bool
    reason: str


class ProductionRetryPolicy:
    RETRYABLE_ERROR_KEYWORDS = [
        "timeout",
        "temporarily unavailable",
        "rate limit",
        "429",
        "500",
        "502",
        "503",
        "504",
        "connection",
        "network",
        "locked",
        "database is locked",
    ]

    NON_RETRYABLE_ERROR_KEYWORDS = [
        "validation",
        "invalid",
        "not found",
        "content_graph_not_found",
        "permission",
        "unauthorized",
        "forbidden",
        "api key",
        "billing",
        "quota",
    ]

    def should_retry(
        self,
        result: PipelineResult,
        attempt: int,
        max_attempts: int,
    ) -> ProductionRetryDecision:
        if attempt >= max_attempts:
            return ProductionRetryDecision(
                should_retry=False,
                reason="max_attempts_reached",
            )

        if result.status == PipelineStatus.COMPLETED:
            return ProductionRetryDecision(
                should_retry=False,
                reason="stage_completed",
            )

        if result.status == PipelineStatus.SKIPPED:
            return ProductionRetryDecision(
                should_retry=False,
                reason="stage_skipped",
            )

        if result.status == PipelineStatus.CANCELLED:
            return ProductionRetryDecision(
                should_retry=False,
                reason="stage_cancelled",
            )

        error_text = str(result.error or "").lower()

        if any(keyword in error_text for keyword in self.NON_RETRYABLE_ERROR_KEYWORDS):
            return ProductionRetryDecision(
                should_retry=False,
                reason="non_retryable_error",
            )

        if any(keyword in error_text for keyword in self.RETRYABLE_ERROR_KEYWORDS):
            return ProductionRetryDecision(
                should_retry=True,
                reason="retryable_stage_error",
            )

        if result.status == PipelineStatus.FAILED:
            return ProductionRetryDecision(
                should_retry=False,
                reason="failed_unknown_non_retryable",
            )

        return ProductionRetryDecision(
            should_retry=False,
            reason="retry_not_required",
        )