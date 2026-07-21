from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path
from uuid import uuid4

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.review.export_api.controller import create_export_workspace_router
from app.review.export_api.service import ExportWorkspaceApplicationService
from app.review.render.checksum import compute_contract_checksum
from app.review.render.contracts import ReviewRenderContract
from app.review.render.submission.contracts import (
    RenderSubmissionReceipt,
    RenderSubmissionResult,
)


class FakeSubmissionRuntime:
    def __init__(self):
        self.calls = 0
        self.last_contract = None

    def try_submit(self, contract, **kwargs):
        self.calls += 1
        self.last_contract = contract

        expected = compute_contract_checksum(contract.canonical_payload())
        if contract.checksum != expected:
            return RenderSubmissionResult(
                success=False,
                error_code="invalid_render_contract",
                error="Review render contract checksum is invalid.",
            )

        return RenderSubmissionResult(
            success=True,
            receipt=RenderSubmissionReceipt(
                queue_job_id="queue-job-16.8.3",
                production_id=contract.production_id,
                snapshot_id=contract.snapshot_id,
                timeline_revision=contract.timeline_revision,
                idempotency_key="idem-16.8.3",
                duplicate=self.calls > 1,
            ),
        )


def build_payload():
    production_id = str(uuid4())
    contract = ReviewRenderContract(
        production_id=production_id,
        timeline_revision=8,
        timeline={
            "production_id": production_id,
            "revision": 8,
            "tracks": [],
        },
        render_options={"format": "mp4", "resolution": "1080p"},
        metadata={"source": "review-workspace"},
    )
    contract = replace(
        contract,
        checksum=compute_contract_checksum(contract.canonical_payload()),
    )
    payload = contract.to_dict()
    payload["requested_by"] = "api-test-user"
    payload["correlation_id"] = "corr-16.8.3"
    return payload


def main():
    runtime = FakeSubmissionRuntime()
    service = ExportWorkspaceApplicationService(runtime)

    app = FastAPI()
    app.include_router(
        create_export_workspace_router(lambda: service)
    )
    client = TestClient(app)

    health = client.get("/api/v1/export-workspace/health")
    assert health.status_code == 200
    assert health.json()["version"] == "16.8.3"

    payload = build_payload()
    first = client.post(
        "/api/v1/export-workspace/render-submissions",
        json=payload,
    )
    assert first.status_code == 202
    first_body = first.json()
    assert first_body["success"] is True
    assert first_body["data"]["queue_job_id"] == "queue-job-16.8.3"
    assert first_body["data"]["duplicate"] is False

    second = client.post(
        "/api/v1/export-workspace/render-submissions",
        json=payload,
    )
    assert second.status_code == 202
    assert second.json()["data"]["duplicate"] is True

    invalid = dict(payload)
    invalid["checksum"] = "tampered"
    rejected = client.post(
        "/api/v1/export-workspace/render-submissions",
        json=invalid,
    )
    assert rejected.status_code == 202
    assert rejected.json()["success"] is False
    assert rejected.json()["error_code"] == "invalid_render_contract"

    malformed = dict(payload)
    malformed.pop("snapshot_id")
    validation = client.post(
        "/api/v1/export-workspace/render-submissions",
        json=malformed,
    )
    assert validation.status_code == 422

    schema = client.get("/openapi.json").json()
    assert (
        "/api/v1/export-workspace/render-submissions"
        in schema["paths"]
    )

    print("SPRINT 16.8.3 EXPORT WORKSPACE API CONTRACTS & CONTROLLER: PASS")
    print("health_endpoint: True")
    print("submission_controller: True")
    print("duplicate_receipt: True")
    print("invalid_contract_mapping: True")
    print("request_validation: True")
    print("openapi_contract: True")


if __name__ == "__main__":
    main()
