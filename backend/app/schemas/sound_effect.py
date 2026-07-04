from __future__ import annotations

from pydantic import BaseModel, Field

from app.db.enums import SoundEffectStatus, SoundEffectType


class SoundEffectPlanCreate(BaseModel):
    production_id: str
    timeline_id: str | None = None


class SoundEffectCueResponse(BaseModel):
    id: str
    asset_id: str | None = None

    start_time: float
    end_time: float

    effect_type: SoundEffectType

    prompt: str | None = None
    keyword: str | None = None
    reason: str | None = None

    metadata_json: str | None = None

    model_config = {
        "from_attributes": True,
    }


class SoundEffectPlanResponse(BaseModel):
    id: str

    production_id: str
    timeline_id: str | None = None

    status: SoundEffectStatus

    metadata_json: str | None = None

    cues: list[SoundEffectCueResponse] = Field(default_factory=list)

    model_config = {
        "from_attributes": True,
    }