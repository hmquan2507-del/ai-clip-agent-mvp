from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.services.story_engine_service import StoryEngineService


class StoryEngineWorker:
    def __init__(self, db: Session):
        self.db = db
        self.service = StoryEngineService(db)

    def run(self, production_id: UUID) -> dict[str, Any]:
        return self.service.run(production_id=production_id)