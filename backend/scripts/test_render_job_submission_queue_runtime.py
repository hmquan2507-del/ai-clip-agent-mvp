from __future__ import annotations

import sys
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from typing import Any
from uuid import uuid4

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.review.render.checksum import compute_contract_checksum
from app.review.render.contracts import ReviewRenderContract
from app.review.render.submission import RenderJobSubmissionRuntime


class InMemoryRenderQueuePort:
    def __init__(self):
        self.jobs: dict[str, dict[str, Any]] = {}
        self.idempotency_index: dict[str, str] = {}
        self.submit_count = 0

    def find_by_idempotency_key(self, idempotency_key: str) -> str | None:
        return self.idempotency_index.get(idempotency_key)

    def submit_render(
        self,
        *,
        production_id: str,
        payload: dict[str, Any],
        idempotency_key: str,
    ) -> str:
        self.submit_count += 1
        job_id = str(uuid4())

        self.jobs[job_id] = {
            "production_id": production_id,
            "payload": deepcopy(payload),
            "idempotency_key": idempotency_key,
        }

        self.idempotency_index[idempotency_key] = job_id
        return job_id


def create_contract() -> ReviewRenderContract:
    production_id = str(uuid4())

    contract = ReviewRenderContract(
        production_id=production_id,
        timeline_revision=7,
        timeline={
            "production_id": production_id,
            "revision": 7,
            "tracks": [
                {
                    "id": "video-1",
                    "type": "video",
                    "clips": [
                        {
                            "id": "clip-1",
                            "start": 0.0,
                            "end": 4.0,
                        }
                    ],
                }
            ],
        },
        render_options={
            "resolution": "1080p",
            "format": "mp4",
        },
        metadata={
            "source": "review-workspace",
        },
    )

    return replace(
        contract,
        checksum=compute_contract_checksum(
            contract.canonical_payload()
        ),
    )


def main() -> None:
    port = InMemoryRenderQueuePort()
    runtime = RenderJobSubmissionRuntime(port)
    contract = create_contract()

    first = runtime.submit(
        contract,
        requested_by="test-user",
    )

    second = runtime.submit(
        contract,
        requested_by="test-user",
    )

    assert first.queue_job_id == second.queue_job_id
    assert first.duplicate is False
    assert second.duplicate is True
    assert port.submit_count == 1

    queued_payload = deepcopy(
        port.jobs[first.queue_job_id]["payload"]
    )

    assert (
        queued_payload["review_render_contract"]["snapshot_id"]
        == contract.snapshot_id
    )
    assert (
        queued_payload["review_render_contract"]["checksum"]
        == contract.checksum
    )
    assert queued_payload["idempotency_key"] == first.idempotency_key

    source_before = deepcopy(contract.timeline)

    queued_payload[
        "review_render_contract"
    ]["timeline"]["tracks"][0]["clips"][0]["end"] = 99

    assert contract.timeline == source_before
    assert (
        port.jobs[first.queue_job_id]["payload"]
        ["review_render_contract"]["timeline"]
        == source_before
    )

    tampered = replace(
        contract,
        timeline={"tracks": []},
    )

    rejected = runtime.try_submit(tampered)

    assert rejected.success is False
    assert rejected.error_code == "invalid_render_contract"
    assert port.submit_count == 1

    print(
        "SPRINT 16.8.2 RENDER JOB SUBMISSION & "
        "QUEUE INTEGRATION: PASS"
    )
    print("single_queue_submission: True")
    print("idempotent_duplicate: True")
    print("immutable_queue_payload: True")
    print("tampered_contract_rejected: True")


if __name__ == "__main__":
    main()
