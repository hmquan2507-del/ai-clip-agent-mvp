from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ExportRenderContractRequest(BaseModel):
    contract_version: str = Field(default="16.8.1")
    snapshot_id: str
    production_id: str
    timeline_revision: int = Field(ge=0)
    timeline: dict[str, Any]
    created_at: str
    render_options: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    checksum: str

    requested_by: str | None = None
    correlation_id: str | None = None


class ExportSubmissionData(BaseModel):
    queue_job_id: str
    production_id: str
    snapshot_id: str
    timeline_revision: int
    idempotency_key: str
    duplicate: bool


class ExportSubmissionResponse(BaseModel):
    success: bool
    data: ExportSubmissionData | None = None
    error_code: str | None = None
    error: str | None = None
