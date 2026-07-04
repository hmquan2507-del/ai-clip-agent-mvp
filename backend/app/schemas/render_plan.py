from __future__ import annotations

from pydantic import BaseModel, Field

from app.db.enums import RenderAssetType, RenderPlanStatus, RenderTrackType


class RenderPlanCreate(BaseModel):
    production_id: str
    timeline_id: str | None = None
    resolution: str = "1080x1920"
    fps: int = 30


class RenderAssetResponse(BaseModel):
    id: str
    asset_id: str | None = None

    type: RenderAssetType

    start_time: float
    end_time: float

    source_start: float | None = None
    source_end: float | None = None

    text: str | None = None
    prompt: str | None = None
    metadata_json: str | None = None

    model_config = {"from_attributes": True}


class RenderTrackResponse(BaseModel):
    id: str

    type: RenderTrackType
    name: str
    position: int

    metadata_json: str | None = None

    assets: list[RenderAssetResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class RenderPlanResponse(BaseModel):
    id: str

    production_id: str
    timeline_id: str | None = None

    status: RenderPlanStatus

    duration_seconds: float
    resolution: str
    fps: int

    metadata_json: str | None = None

    tracks: list[RenderTrackResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}