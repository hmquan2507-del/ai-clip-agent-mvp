from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.services.ai_engine_runtime_service import AIEngineRuntimeService


class EmotionEngineService:
    ENGINE_KEY = "emotion_engine"

    def __init__(self, db: Session):
        self.runtime_service = AIEngineRuntimeService(db)

    def run(self, production_id: UUID) -> dict[str, Any]:
        return self.runtime_service.run_engine(
            production_id=production_id,
            engine_key=self.ENGINE_KEY,
        )