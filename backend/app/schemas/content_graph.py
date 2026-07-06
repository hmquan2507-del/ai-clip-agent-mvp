from __future__ import annotations

from pydantic import BaseModel, Field

from app.db.enums import ContentEmotion, ContentGraphStatus, ContentSegmentType


class ContentSegmentResponse(BaseModel):
    id: str
    start_time: float
    end_time: float
    type: ContentSegmentType
    emotion: ContentEmotion
    topic: str | None = None
    text: str
    importance_score: float
    viral_potential_score: float
    speaker_id: str | None = None
    order_index: int
    metadata_json: str | None = None

    model_config = {"from_attributes": True}


class ContentGraphResponse(BaseModel):
    id: str
    production_id: str
    status: ContentGraphStatus
    language: str | None = None
    summary: str | None = None
    topic_json: str | None = None
    speaker_json: str | None = None
    metadata_json: str | None = None
    segments: list[ContentSegmentResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}