from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.db.enums import UploadStatus


class UploadRead(BaseModel):
    id: UUID
    production_id: UUID
    filename: str
    mime_type: str | None
    size_bytes: int | None
    storage_path: str
    status: UploadStatus
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }