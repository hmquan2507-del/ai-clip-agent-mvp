from pydantic import BaseModel, Field

from app.db.enums import EditingPlanItemAction, EditingPlanStatus


class EditingPlanCreate(BaseModel):
    production_id: str
    provider: str | None = "gemini"


class EditingPlanItemResponse(BaseModel):
    id: str
    start_time: float
    end_time: float
    action: EditingPlanItemAction
    reason: str | None = None
    priority: int
    metadata_json: str | None = None

    model_config = {"from_attributes": True}


class EditingPlanResponse(BaseModel):
    id: str
    production_id: str
    status: EditingPlanStatus
    provider: str | None = None
    summary: str | None = None
    items: list[EditingPlanItemResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}