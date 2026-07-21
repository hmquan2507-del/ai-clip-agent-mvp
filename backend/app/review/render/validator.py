from __future__ import annotations

from app.review.render.checksum import compute_contract_checksum
from app.review.render.contracts import ReviewRenderContract
from app.review.render.errors import (
    InvalidRenderSnapshotError,
    RenderSnapshotChecksumError,
    TimelineRevisionMismatchError,
)


class ReviewRenderContractValidator:
    def validate(self, contract: ReviewRenderContract, *, expected_revision: int | None = None) -> None:
        if not contract.production_id.strip():
            raise InvalidRenderSnapshotError("production_id is required.")
        if contract.timeline_revision < 1:
            raise InvalidRenderSnapshotError("timeline_revision must be positive.")
        if expected_revision is not None and contract.timeline_revision != expected_revision:
            raise TimelineRevisionMismatchError("Timeline revision does not match the requested revision.")
        timeline = contract.timeline
        if timeline.get("production_id") != contract.production_id:
            raise InvalidRenderSnapshotError("Snapshot production_id does not match contract.")
        if int(timeline.get("revision", -1)) != contract.timeline_revision:
            raise InvalidRenderSnapshotError("Snapshot revision does not match contract.")
        expected = compute_contract_checksum(contract.canonical_payload())
        if contract.checksum != expected:
            raise RenderSnapshotChecksumError("Render snapshot checksum is invalid.")
