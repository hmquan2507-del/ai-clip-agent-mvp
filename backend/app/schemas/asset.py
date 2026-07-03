from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.db.enums import AssetType


class AssetRead(BaseModel):
    id: UUID
    production_id: UUID
    type: AssetType
    filename: str
    mime_type: str | None
    size_bytes: int | None
    storage_path: str
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
    version: int | None = None

    model_config = {
        "from_attributes": True,
    }