from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.db.enums import QueueStatus, QueueType


class QueueRead(BaseModel):
    id: UUID
    production_id: UUID
    type: QueueType
    status: QueueStatus
    progress: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {
        "from_attributes": True,
    }