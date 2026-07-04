from __future__ import annotations

from sqlalchemy.orm import Session, selectinload

from app.db.enums import SoundEffectStatus, SoundEffectType
from app.db.models.sound_effect import (
    SoundEffectCue,
    SoundEffectPlan,
)


class SoundEffectRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_plan(
        self,
        production_id: str,
        timeline_id: str | None = None,
    ) -> SoundEffectPlan:

        plan = SoundEffectPlan(
            production_id=production_id,
            timeline_id=timeline_id,
            status=SoundEffectStatus.PROCESSING,
        )

        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)

        return plan

    def get_by_id(
        self,
        plan_id: str,
    ) -> SoundEffectPlan | None:

        return (
            self.db.query(SoundEffectPlan)
            .options(selectinload(SoundEffectPlan.cues))
            .filter(SoundEffectPlan.id == plan_id)
            .first()
        )

    def get_latest_by_production(
        self,
        production_id: str,
    ) -> SoundEffectPlan | None:

        return (
            self.db.query(SoundEffectPlan)
            .options(selectinload(SoundEffectPlan.cues))
            .filter(
                SoundEffectPlan.production_id == production_id,
            )
            .order_by(
                SoundEffectPlan.created_at.desc(),
            )
            .first()
        )

    def add_cue(
        self,
        sound_effect_plan_id: str,
        start_time: float,
        end_time: float,
        effect_type: SoundEffectType,
        asset_id: str | None = None,
        prompt: str | None = None,
        keyword: str | None = None,
        reason: str | None = None,
        metadata_json: str | None = None,
    ) -> SoundEffectCue:

        cue = SoundEffectCue(
            sound_effect_plan_id=sound_effect_plan_id,
            asset_id=asset_id,
            start_time=start_time,
            end_time=end_time,
            effect_type=effect_type,
            prompt=prompt,
            keyword=keyword,
            reason=reason,
            metadata_json=metadata_json,
        )

        self.db.add(cue)
        self.db.commit()
        self.db.refresh(cue)

        return cue

    def mark_completed(
        self,
        plan_id: str,
        metadata_json: str | None = None,
    ) -> SoundEffectPlan:

        plan = self.get_by_id(plan_id)

        if plan is None:
            raise ValueError("Sound effect plan not found")

        plan.status = SoundEffectStatus.COMPLETED
        plan.metadata_json = metadata_json

        self.db.commit()
        self.db.refresh(plan)

        return plan

    def mark_failed(
        self,
        plan_id: str,
        error_message: str,
    ) -> SoundEffectPlan:

        plan = self.get_by_id(plan_id)

        if plan is None:
            raise ValueError("Sound effect plan not found")

        plan.status = SoundEffectStatus.FAILED
        plan.metadata_json = error_message

        self.db.commit()
        self.db.refresh(plan)

        return plan

    def delete_by_production(
        self,
        production_id: str,
    ) -> bool:

        plan = self.get_latest_by_production(
            production_id,
        )

        if plan is None:
            return False

        self.db.delete(plan)
        self.db.commit()

        return True