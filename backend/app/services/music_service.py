from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.db.enums import MusicMood
from app.repositories.music_repository import MusicRepository
from app.repositories.timeline_repository import TimelineRepository
from app.services.base_runtime_service import BaseRuntimeService
from app.services.music_engine import MusicEngine


class MusicService(BaseRuntimeService):
    def __init__(self, db: Session):
        super().__init__(db)

        self.timeline_repo = TimelineRepository(db)
        self.music_repo = MusicRepository(db)
        self.music_engine = MusicEngine()

    def generate_music_plan(
        self,
        production_id: UUID,
        mood: MusicMood = MusicMood.CUSTOM,
    ):
        self.ensure_production_exists(production_id)

        timeline = self.timeline_repo.get_latest_by_production(
            production_id=str(production_id),
        )

        if timeline is None:
            self.raise_missing_dependency("Timeline not found")

        result = self.music_engine.build_from_timeline(
            timeline=timeline,
            mood=mood,
        )

        plan = self.music_repo.create_plan(
            production_id=str(production_id),
            timeline_id=timeline.id,
            mood=result["mood"],
        )

        try:
            for cue in result["cues"]:
                self.music_repo.add_cue(
                    music_plan_id=plan.id,
                    start_time=cue["start_time"],
                    end_time=cue["end_time"],
                    mood=cue["mood"],
                    prompt=cue["prompt"],
                    keyword=cue["keyword"],
                    volume=cue["volume"],
                    fade_in=cue["fade_in"],
                    fade_out=cue["fade_out"],
                    metadata_json=cue["metadata_json"],
                )

            return self.music_repo.mark_completed(
                plan_id=plan.id,
                metadata_json=self.music_engine.dumps_metadata(
                    result.get("metadata")
                ),
            )

        except Exception as exc:
            self.music_repo.mark_failed(
                plan_id=plan.id,
                error_message=str(exc),
            )
            raise

    def get_latest_music_plan(self, production_id: UUID):
        plan = self.music_repo.get_latest_by_production(
            production_id=str(production_id),
        )

        if plan is None:
            self.raise_not_found("Music plan not found")

        return plan

    def delete_latest_music_plan(self, production_id: UUID) -> bool:
        deleted = self.music_repo.delete_by_production(
            production_id=str(production_id),
        )

        if not deleted:
            self.raise_not_found("Music plan not found")

        return True