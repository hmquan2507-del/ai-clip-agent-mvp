from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.sound_effect_repository import SoundEffectRepository
from app.repositories.timeline_repository import TimelineRepository
from app.services.base_runtime_service import BaseRuntimeService
from app.services.sound_effect_engine import SoundEffectEngine


class SoundEffectService(BaseRuntimeService):
    def __init__(self, db: Session):
        super().__init__(db)

        self.timeline_repo = TimelineRepository(db)
        self.sound_effect_repo = SoundEffectRepository(db)
        self.sound_effect_engine = SoundEffectEngine()

    def generate_sound_effect_plan(self, production_id: UUID):
        self.ensure_production_exists(production_id)

        timeline = self.timeline_repo.get_latest_by_production(
            production_id=str(production_id),
        )

        if timeline is None:
            self.raise_missing_dependency("Timeline not found")

        plan = self.sound_effect_repo.create_plan(
            production_id=str(production_id),
            timeline_id=timeline.id,
        )

        try:
            result = self.sound_effect_engine.build_from_timeline(timeline)

            for cue in result["cues"]:
                self.sound_effect_repo.add_cue(
                    sound_effect_plan_id=plan.id,
                    start_time=cue["start_time"],
                    end_time=cue["end_time"],
                    effect_type=cue["effect_type"],
                    prompt=cue["prompt"],
                    keyword=cue["keyword"],
                    reason=cue["reason"],
                    metadata_json=cue["metadata_json"],
                )

            return self.sound_effect_repo.mark_completed(
                plan_id=plan.id,
                metadata_json=self.sound_effect_engine.dumps_metadata(
                    result.get("metadata")
                ),
            )

        except Exception as exc:
            self.sound_effect_repo.mark_failed(
                plan_id=plan.id,
                error_message=str(exc),
            )
            raise

    def get_latest_sound_effect_plan(self, production_id: UUID):
        plan = self.sound_effect_repo.get_latest_by_production(
            production_id=str(production_id),
        )

        if plan is None:
            self.raise_not_found("Sound effect plan not found")

        return plan

    def delete_latest_sound_effect_plan(self, production_id: UUID) -> bool:
        deleted = self.sound_effect_repo.delete_by_production(
            production_id=str(production_id),
        )

        if not deleted:
            self.raise_not_found("Sound effect plan not found")

        return True