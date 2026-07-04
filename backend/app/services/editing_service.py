from __future__ import annotations

import json
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.enums import EditingPlanItemAction
from app.repositories.editing_plan_repository import EditingPlanRepository
from app.repositories.production_repository import ProductionRepository
from app.repositories.queue_repository import QueueRepository
from app.services.editing_engine import EditingEngine

class EditingService:
    def __init__(self, db: Session):
        self.editing_engine = EditingEngine()
        self.db = db
        self.production_repo = ProductionRepository(db)
        self.queue_repo = QueueRepository(db)
        self.editing_plan_repo = EditingPlanRepository(db)

    async def generate_editing_plan(
        self,
        production_id: UUID,
        provider: str | None = "gemini",
        target_duration_seconds: int | None = None,
    ):
        production = self.production_repo.get_by_id(production_id)

        if production is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Production not found",
            )

        transcript_text = self._get_latest_transcript_text(production_id)

        plan = self.editing_plan_repo.create_plan(
            production_id=str(production_id),
            provider=provider,
        )

        try:

            result = await self.editing_engine.generate(
            production_id=str(production_id),
            transcript=transcript_text,
            provider=provider,
            target_duration_seconds=target_duration_seconds,
            )   

            self._save_provider_result(
                plan_id=plan.id,
                result=result,
            )

            return self.editing_plan_repo.mark_completed(
                plan_id=plan.id,
                summary=result.get("summary"),
            )

        except Exception as exc:
            self.editing_plan_repo.mark_failed(
                plan_id=plan.id,
                error_message=str(exc),
            )
            raise

    def get_latest_plan(self, production_id: UUID):
        plan = self.editing_plan_repo.get_latest_by_production(
            production_id=str(production_id),
        )

        if plan is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Editing plan not found",
            )

        return plan

    def delete_latest_plan(self, production_id: UUID) -> bool:
        deleted = self.editing_plan_repo.delete_by_production(
            production_id=str(production_id),
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Editing plan not found",
            )

        return True
    def _get_latest_transcript_text(self, production_id: UUID) -> str:
        job = self.queue_repo.get_latest_completed_transcript(
            production_id=production_id,
        )

        if job is None or not job.result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Completed transcript result not found",
            )

        try:
            result = json.loads(job.result)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Invalid transcript result format: {exc}",
            ) from exc

        transcript_text = result.get("text")

        if not transcript_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transcript text is empty",
            )

        return transcript_text
    def _save_provider_result(
        self,
        plan_id: str,
        result: dict,
    ) -> None:
        segments = result.get("segments", [])

        for segment in segments:
            action = self._normalize_action(segment.get("action"))

            self.editing_plan_repo.add_item(
                plan_id=plan_id,
                start_time=float(segment.get("start_time", 0)),
                end_time=float(segment.get("end_time", 0)),
                action=action,
                reason=segment.get("reason"),
                priority=int(segment.get("priority", 0)),
                metadata_json=str(segment.get("metadata", {})),
            )

    def _normalize_action(self, action: str | None) -> EditingPlanItemAction:
        if not action:
            return EditingPlanItemAction.KEEP

        normalized = action.lower()

        for item_action in EditingPlanItemAction:
            if item_action.value == normalized:
                return item_action

        return EditingPlanItemAction.KEEP