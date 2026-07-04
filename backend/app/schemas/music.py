from __future__ import annotations

from pydantic import BaseModel, Field

from app.db.enums import MusicMood, MusicStatus


class MusicPlanCreate(BaseModel):
    production_id: str
    timeline_id: str | None = None
    mood: MusicMood = MusicMood.CUSTOM


class MusicCueResponse(BaseModel):
    id: str
    asset_id: str | None = None

    start_time: float
    end_time: float

    mood: MusicMood
    prompt: str | None = None
    keyword: str | None = None

    volume: float
    fade_in: float
    fade_out: float

    metadata_json: str | None = None

    model_config = {"from_attributes": True}


class MusicPlanResponse(BaseModel):
    id: str

    production_id: str
    timeline_id: str | None = None

    status: MusicStatus
    mood: MusicMood

    metadata_json: str | None = None
    cues: list[MusicCueResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}