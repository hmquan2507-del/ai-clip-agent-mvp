from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.editing_plan_repository import EditingPlanRepository
from app.repositories.production_repository import ProductionRepository
from app.repositories.timeline_repository import TimelineRepository
from app.services.timeline_engine import TimelineEngine


class TimelineService:
    def __init__(self, db: Session):
        self.db = db
        self.production_repo = ProductionRepository(db)
        self.editing_plan_repo = EditingPlanRepository(db)
        self.timeline_repo = TimelineRepository(db)
        self.timeline_engine = TimelineEngine()

    def generate_timeline(self, production_id: UUID):
        production = self.production_repo.get_by_id(production_id)

        if production is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Production not found",
            )

        editing_plan = self.editing_plan_repo.get_latest_by_production(
            production_id=str(production_id),
        )

        if editing_plan is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Editing plan not found",
            )

        timeline = self.timeline_repo.create_timeline(
            production_id=str(production_id),
            editing_plan_id=editing_plan.id,
        )

        try:
            timeline_data = self.timeline_engine.build_from_editing_plan(
                editing_plan=editing_plan,
            )

            for track_data in timeline_data["tracks"]:
                track = self.timeline_repo.add_track(
                    timeline_id=timeline.id,
                    track_type=track_data["type"],
                    name=track_data["name"],
                    position=track_data["position"],
                )

                for clip_data in track_data["clips"]:
                    self.timeline_repo.add_clip(
                        track_id=track.id,
                        clip_type=clip_data["type"],
                        timeline_start=clip_data["timeline_start"],
                        timeline_end=clip_data["timeline_end"],
                        source_start=clip_data.get("source_start"),
                        source_end=clip_data.get("source_end"),
                        text=clip_data.get("text"),
                        metadata_json=self.timeline_engine.dumps_metadata(
                            clip_data.get("metadata")
                        ),
                    )

            return self.timeline_repo.mark_completed(
                timeline_id=timeline.id,
                duration_seconds=timeline_data["duration_seconds"],
            )

        except Exception as exc:
            self.timeline_repo.mark_failed(
                timeline_id=timeline.id,
                error_message=str(exc),
            )
            raise

    def get_latest_timeline(self, production_id: UUID):
        timeline = self.timeline_repo.get_latest_by_production(
            production_id=str(production_id),
        )

        if timeline is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Timeline not found",
            )

        return timeline

    def delete_latest_timeline(self, production_id: UUID) -> bool:
        deleted = self.timeline_repo.delete_by_production(
            production_id=str(production_id),
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Timeline not found",
            )

        return True