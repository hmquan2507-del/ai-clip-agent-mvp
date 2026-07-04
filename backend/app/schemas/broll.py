from __future__ import annotations

from pydantic import BaseModel, Field

from app.db.enums import BrollSourceType, BrollStatus


class BrollPlanCreate(BaseModel):
    production_id: str
    timeline_id: str | None = None


class BrollCueResponse(BaseModel):
    id: str
    asset_id: str | None = None
    start_time: float
    end_time: float
    source_type: BrollSourceType
    prompt: str | None = None
    keyword: str | None = None
    reason: str | None = None
    metadata_json: str | None = None

    model_config = {"from_attributes": True}


class BrollPlanResponse(BaseModel):
    id: str
    production_id: str
    timeline_id: str | None = None
    status: BrollStatus
    metadata_json: str | None = None
    cues: list[BrollCueResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}