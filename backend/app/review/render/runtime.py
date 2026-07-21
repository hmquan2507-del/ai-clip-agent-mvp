from __future__ import annotations

from dataclasses import replace
from typing import Any

from app.review.editing.state.store import TimelineRuntimeStore
from app.review.render.checksum import compute_contract_checksum
from app.review.render.contracts import ReviewRenderContract, ReviewRenderHandoffResult
from app.review.render.errors import DirtyTimelineError, ReviewRenderHandoffError, TimelineRevisionMismatchError
from app.review.render.mapper import ReviewTimelineRenderMapper
from app.review.render.validator import ReviewRenderContractValidator


class ReviewToRenderHandoffRuntime:
    def __init__(self, store: TimelineRuntimeStore, *, mapper: ReviewTimelineRenderMapper | None = None, validator: ReviewRenderContractValidator | None = None):
        self.store = store
        self.mapper = mapper or ReviewTimelineRenderMapper()
        self.validator = validator or ReviewRenderContractValidator()

    def create_contract(self, *, expected_revision: int | None = None, render_options: dict[str, Any] | None = None, metadata: dict[str, Any] | None = None, require_clean: bool = True) -> ReviewRenderContract:
        timeline = self.store.snapshot()
        if require_clean and timeline.dirty:
            raise DirtyTimelineError("Timeline must be saved before render handoff.")
        if expected_revision is not None and timeline.revision != expected_revision:
            raise TimelineRevisionMismatchError("Timeline revision does not match the requested revision.")
        contract = ReviewRenderContract(
            production_id=timeline.production_id,
            timeline_revision=timeline.revision,
            timeline=self.mapper.map(timeline),
            render_options=dict(render_options or {}),
            metadata=dict(metadata or {}),
        )
        contract = replace(contract, checksum=compute_contract_checksum(contract.canonical_payload()))
        self.validator.validate(contract, expected_revision=expected_revision)
        return contract

    def handoff(self, **kwargs: Any) -> ReviewRenderHandoffResult:
        try:
            return ReviewRenderHandoffResult(success=True, contract=self.create_contract(**kwargs))
        except ReviewRenderHandoffError as exc:
            return ReviewRenderHandoffResult(success=False, error_code=exc.code, error=str(exc))
