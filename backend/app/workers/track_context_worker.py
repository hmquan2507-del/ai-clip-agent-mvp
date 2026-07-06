from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.services.track_context_service import TrackContextService


class TrackContextWorker:
    def __init__(self, db: Session):
        self.service = TrackContextService(db)

    def run(self, production_id: UUID) -> dict[str, Any]:
        return self.service.run(production_id=production_id)