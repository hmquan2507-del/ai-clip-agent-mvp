from __future__ import annotations

from pydantic import BaseModel, Field

from app.db.enums import SubtitleStatus, SubtitleStyle


class SubtitleCreate(BaseModel):
    production_id: str
    timeline_id: str | None = None
    style: SubtitleStyle = SubtitleStyle.DEFAULT
    language: str | None = None


class SubtitleCueResponse(BaseModel):
    id: str
    start_time: float
    end_time: float
    text: str
    style_json: str | None = None

    model_config = {"from_attributes": True}


class SubtitleResponse(BaseModel):
    id: str
    production_id: str
    timeline_id: str | None = None
    status: SubtitleStatus
    style: SubtitleStyle
    language: str | None = None
    metadata_json: str | None = None
    cues: list[SubtitleCueResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}