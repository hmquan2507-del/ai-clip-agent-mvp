from __future__ import annotations

from pydantic import BaseModel, Field

from app.db.enums import TimelineClipType, TimelineStatus, TimelineTrackType


class TimelineCreate(BaseModel):
    production_id: str
    editing_plan_id: str | None = None


class TimelineClipResponse(BaseModel):
    id: str
    asset_id: str | None = None
    source_start: float | None = None
    source_end: float | None = None
    timeline_start: float
    timeline_end: float
    type: TimelineClipType
    text: str | None = None
    metadata_json: str | None = None

    model_config = {"from_attributes": True}


class TimelineTrackResponse(BaseModel):
    id: str
    type: TimelineTrackType
    name: str
    position: int
    metadata_json: str | None = None
    clips: list[TimelineClipResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class TimelineResponse(BaseModel):
    id: str
    production_id: str
    editing_plan_id: str | None = None
    status: TimelineStatus
    duration_seconds: float
    version: int
    metadata_json: str | None = None
    tracks: list[TimelineTrackResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}