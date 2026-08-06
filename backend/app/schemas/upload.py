from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UploadRead(BaseModel):
    id: UUID
    production_id: UUID
    filename: str
    mime_type: str | None
    size_bytes: int | None
    storage_path: str
    duration: float | None
    width: int | None
    height: int | None
    fps: float | None
    video_codec: str | None
    audio_codec: str | None
    has_audio: bool | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }