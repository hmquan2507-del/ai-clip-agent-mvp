from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.enums import BrollSourceType
from app.repositories.broll_repository import BrollRepository
from app.repositories.production_repository import ProductionRepository
from app.repositories.timeline_repository import TimelineRepository
from app.services.broll_engine import BrollEngine


class BrollService:
    def __init__(self, db: Session):
        self.db = db
        self.production_repo = ProductionRepository(db)
        self.timeline_repo = TimelineRepository(db)
        self.broll_repo = BrollRepository(db)
        self.broll_engine = BrollEngine()

    def generate_broll_plan(self, production_id: UUID):
        production = self.production_repo.get_by_id(production_id)

        if production is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Production not found",
            )

        timeline = self.timeline_repo.get_latest_by_production(
            production_id=str(production_id),
        )

        if timeline is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Timeline not found",
            )

        plan = self.broll_repo.create_plan(
            production_id=str(production_id),
            timeline_id=timeline.id,
        )

        try:
            result = self.broll_engine.build_from_timeline(timeline)

            for cue in result["cues"]:
                self.broll_repo.add_cue(
                    broll_plan_id=plan.id,
                    start_time=cue["start_time"],
                    end_time=cue["end_time"],
                    source_type=BrollSourceType.SUGGESTION,
                    prompt=cue["prompt"],
                    keyword=cue["keyword"],
                    reason=cue["reason"],
                    metadata_json=cue["metadata_json"],
                )

            return self.broll_repo.mark_completed(
                plan_id=plan.id,
                metadata_json=self.broll_engine.dumps_metadata(
                    result.get("metadata")
                ),
            )

        except Exception as exc:
            self.broll_repo.mark_failed(
                plan_id=plan.id,
                error_message=str(exc),
            )
            raise

    def get_latest_broll_plan(self, production_id: UUID):
        plan = self.broll_repo.get_latest_by_production(
            production_id=str(production_id),
        )

        if plan is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="B-roll plan not found",
            )

        return plan

    def delete_latest_broll_plan(self, production_id: UUID) -> bool:
        deleted = self.broll_repo.delete_by_production(
            production_id=str(production_id),
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="B-roll plan not found",
            )

        return True