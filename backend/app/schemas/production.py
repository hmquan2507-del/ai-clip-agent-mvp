from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.db.enums import ProductionStatus


class ProductionBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    style: str | None = None


class ProductionCreate(ProductionBase):
    workspace_id: UUID


class ProductionUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    style: str | None = None
    status: ProductionStatus | None = None
    progress: int | None = Field(default=None, ge=0, le=100)


class ProductionRead(ProductionBase):
    id: UUID
    workspace_id: UUID
    status: ProductionStatus
    progress: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    version: int

    model_config = {
        "from_attributes": True,
    }