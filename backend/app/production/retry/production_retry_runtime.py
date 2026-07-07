from __future__ import annotations

import time
from typing import Callable

from app.production.contracts import PipelineResult, PipelineStage, PipelineStatus
from app.production.retry.production_retry_history import ProductionRetryHistoryItem
from app.production.retry.production_retry_policy import ProductionRetryPolicy
from app.production.retry.production_retry_result import ProductionRetryResult


class ProductionRetryRuntime:
    def __init__(
        self,
        policy: ProductionRetryPolicy | None = None,
        max_attempts: int = 3,
        sleep_seconds: float = 0.5,
    ):
        self.policy = policy or ProductionRetryPolicy()
        self.max_attempts = max_attempts
        self.sleep_seconds = sleep_seconds
        self.history: list[ProductionRetryHistoryItem] = []

    def run_stage(
        self,
        production_id: str,
        stage: PipelineStage,
        call: Callable[[], PipelineResult],
    ) -> ProductionRetryResult:
        retry_reasons: list[str] = []

        last_result: PipelineResult | None = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                result = call()
            except Exception as error:
                result = PipelineResult(
                    production_id=production_id,
                    stage=stage,
                    status=PipelineStatus.FAILED,
                    payload={},
                    error=str(error),
                    metadata={
                        "exception_class": error.__class__.__name__,
                    },
                )

            last_result = result

            decision = self.policy.should_retry(
                result=result,
                attempt=attempt,
                max_attempts=self.max_attempts,
            )

            self.history.append(
                ProductionRetryHistoryItem(
                    stage=stage,
                    attempt=attempt,
                    status=result.status,
                    reason=decision.reason,
                    error=result.error,
                )
            )

            if not decision.should_retry:
                return ProductionRetryResult(
                    production_id=production_id,
                    stage=stage,
                    status=result.status,
                    result=result,
                    attempts=attempt,
                    retried=attempt > 1,
                    retry_reasons=retry_reasons,
                    metadata={
                        "final_decision": decision.reason,
                    },
                )

            retry_reasons.append(decision.reason)
            time.sleep(self.sleep_seconds * attempt)

        return ProductionRetryResult(
            production_id=production_id,
            stage=stage,
            status=last_result.status if last_result else PipelineStatus.FAILED,
            result=last_result,
            attempts=self.max_attempts,
            retried=True,
            retry_reasons=retry_reasons,
            metadata={
                "final_decision": "retry_exhausted",
            },
        )

    def history_to_list(self) -> list[dict]:
        return [item.to_dict() for item in self.history]