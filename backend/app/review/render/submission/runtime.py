from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.review.render.checksum import compute_contract_checksum
from app.review.render.contracts import ReviewRenderContract
from app.review.render.submission.contracts import (
    RenderSubmissionReceipt,
    RenderSubmissionRequest,
    RenderSubmissionResult,
)
from app.review.render.submission.errors import (
    InvalidRenderContractSubmissionError,
    RenderQueueSubmissionError,
    RenderSubmissionError,
)
from app.review.render.submission.ports import RenderQueueSubmissionPort
from app.review.render.validator import ReviewRenderContractValidator


class RenderJobSubmissionRuntime:
    """Submit immutable ReviewRenderContract payloads to the render queue.

    The runtime never reads TimelineRuntimeStore. It accepts only the frozen
    contract produced by Sprint 16.8.1.
    """

    def __init__(
        self,
        queue_port: RenderQueueSubmissionPort,
        *,
        validator: ReviewRenderContractValidator | None = None,
    ):
        self.queue_port = queue_port
        self.validator = validator or ReviewRenderContractValidator()

    def submit(
        self,
        contract: ReviewRenderContract,
        *,
        requested_by: str | None = None,
        correlation_id: str | None = None,
    ) -> RenderSubmissionReceipt:
        self._validate_contract(contract)

        request = RenderSubmissionRequest(
            contract_payload=deepcopy(contract.to_dict()),
            requested_by=requested_by,
            correlation_id=correlation_id,
        )

        existing_job_id = self.queue_port.find_by_idempotency_key(
            request.idempotency_key
        )
        if existing_job_id is not None:
            return self._receipt(
                queue_job_id=existing_job_id,
                contract=contract,
                idempotency_key=request.idempotency_key,
                duplicate=True,
            )

        try:
            queue_job_id = self.queue_port.submit_render(
                production_id=contract.production_id,
                payload=request.to_queue_payload(),
                idempotency_key=request.idempotency_key,
            )
        except RenderSubmissionError:
            raise
        except Exception as exc:
            raise RenderQueueSubmissionError(
                "Render queue rejected the submission."
            ) from exc

        return self._receipt(
            queue_job_id=str(queue_job_id),
            contract=contract,
            idempotency_key=request.idempotency_key,
            duplicate=False,
        )

    def try_submit(
        self,
        contract: ReviewRenderContract,
        **kwargs: Any,
    ) -> RenderSubmissionResult:
        try:
            return RenderSubmissionResult(
                success=True,
                receipt=self.submit(contract, **kwargs),
            )
        except RenderSubmissionError as exc:
            return RenderSubmissionResult(
                success=False,
                error_code=exc.code,
                error=str(exc),
            )

    def _validate_contract(self, contract: ReviewRenderContract) -> None:
        try:
            self.validator.validate(
                contract,
                expected_revision=contract.timeline_revision,
            )
        except Exception as exc:
            raise InvalidRenderContractSubmissionError(str(exc)) from exc

        expected_checksum = compute_contract_checksum(contract.canonical_payload())
        if contract.checksum != expected_checksum:
            raise InvalidRenderContractSubmissionError(
                "Review render contract checksum is invalid."
            )

    @staticmethod
    def _receipt(
        *,
        queue_job_id: str,
        contract: ReviewRenderContract,
        idempotency_key: str,
        duplicate: bool,
    ) -> RenderSubmissionReceipt:
        return RenderSubmissionReceipt(
            queue_job_id=str(queue_job_id),
            production_id=contract.production_id,
            snapshot_id=contract.snapshot_id,
            timeline_revision=contract.timeline_revision,
            idempotency_key=idempotency_key,
            duplicate=duplicate,
        )
