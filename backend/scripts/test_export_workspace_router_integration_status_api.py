from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from uuid import uuid4

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.review.export_api.router import (
    get_export_render_status_service,
    router,
)
from app.review.export_api.status import ExportRenderStatusService


class FakeStatus(str, Enum):
    RUNNING = "running"


class FakeQueueType(str, Enum):
    RENDER_RUNTIME = "render_runtime"


@dataclass
class FakeJob:
    id: object
    production_id: object
    queue_type: FakeQueueType
    status: FakeStatus
    progress: int
    error_message: str | None
    created_at: datetime
    started_at: datetime
    finished_at: datetime | None
    updated_at: datetime


class FakeQueueService:
    def __init__(self, job):
        self.job = job

    def get(self, queue_id):
        if str(queue_id) != str(self.job.id):
            raise HTTPException(status_code=404, detail="Queue job not found")
        return self.job


def main() -> None:
    queue_job_id = uuid4()
    production_id = uuid4()
    now = datetime.now(timezone.utc)

    job = FakeJob(
        id=queue_job_id,
        production_id=production_id,
        queue_type=FakeQueueType.RENDER_RUNTIME,
        status=FakeStatus.RUNNING,
        progress=42,
        error_message=None,
        created_at=now,
        started_at=now,
        finished_at=None,
        updated_at=now,
    )

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_export_render_status_service] = (
        lambda: ExportRenderStatusService(FakeQueueService(job))
    )

    client = TestClient(app)

    health = client.get("/api/v1/export-workspace/health")
    assert health.status_code == 200
    assert health.json()["version"] == "16.8.4"

    response = client.get(
        f"/api/v1/export-workspace/render-submissions/{queue_job_id}"
    )
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["data"]["queue_job_id"] == str(queue_job_id)
    assert body["data"]["production_id"] == str(production_id)
    assert body["data"]["queue_type"] == "render_runtime"
    assert body["data"]["status"] == "running"
    assert body["data"]["progress"] == 42
    assert body["data"]["error"] is None

    missing = client.get(
        f"/api/v1/export-workspace/render-submissions/{uuid4()}"
    )
    assert missing.status_code == 404

    malformed = client.get(
        "/api/v1/export-workspace/render-submissions/not-a-uuid"
    )
    assert malformed.status_code == 422

    schema = client.get("/openapi.json").json()
    status_path = (
        "/api/v1/export-workspace/render-submissions/{queue_job_id}"
    )
    assert status_path in schema["paths"]

    main_source = (BACKEND_ROOT / "app" / "main.py").read_text(
        encoding="utf-8"
    )
    assert (
        "from app.review.export_api.router import "
        "router as export_workspace_router"
    ) in main_source
    assert "app.include_router(export_workspace_router)" in main_source

    print(
        "SPRINT 16.8.4 EXPORT WORKSPACE ROUTER INTEGRATION "
        "& RENDER STATUS API: PASS"
    )
    print("root_router_integrated: True")
    print("render_status_endpoint: True")
    print("status_projection: True")
    print("missing_job_404: True")
    print("invalid_uuid_422: True")
    print("openapi_status_contract: True")


if __name__ == "__main__":
    main()
