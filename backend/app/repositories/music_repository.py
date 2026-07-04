from __future__ import annotations

from sqlalchemy.orm import Session, selectinload

from app.db.enums import MusicMood, MusicStatus
from app.db.models.music import MusicCue, MusicPlan


class MusicRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_plan(
        self,
        production_id: str,
        timeline_id: str | None = None,
        mood: MusicMood = MusicMood.CUSTOM,
    ) -> MusicPlan:
        plan = MusicPlan(
            production_id=production_id,
            timeline_id=timeline_id,
            status=MusicStatus.PROCESSING,
            mood=mood,
        )

        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)

        return plan

    def get_by_id(
        self,
        plan_id: str,
    ) -> MusicPlan | None:
        return (
            self.db.query(MusicPlan)
            .options(selectinload(MusicPlan.cues))
            .filter(MusicPlan.id == plan_id)
            .first()
        )

    def get_latest_by_production(
        self,
        production_id: str,
    ) -> MusicPlan | None:
        return (
            self.db.query(MusicPlan)
            .options(selectinload(MusicPlan.cues))
            .filter(MusicPlan.production_id == production_id)
            .order_by(MusicPlan.created_at.desc())
            .first()
        )

    def add_cue(
        self,
        music_plan_id: str,
        start_time: float,
        end_time: float,
        mood: MusicMood,
        asset_id: str | None = None,
        prompt: str | None = None,
        keyword: str | None = None,
        volume: float = 0.35,
        fade_in: float = 1.0,
        fade_out: float = 1.0,
        metadata_json: str | None = None,
    ) -> MusicCue:
        cue = MusicCue(
            music_plan_id=music_plan_id,
            asset_id=asset_id,
            start_time=start_time,
            end_time=end_time,
            mood=mood,
            prompt=prompt,
            keyword=keyword,
            volume=volume,
            fade_in=fade_in,
            fade_out=fade_out,
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
    ) -> MusicPlan:
        plan = self.get_by_id(plan_id)

        if plan is None:
            raise ValueError("Music plan not found")

        plan.status = MusicStatus.COMPLETED
        plan.metadata_json = metadata_json

        self.db.commit()
        self.db.refresh(plan)

        return plan

    def mark_failed(
        self,
        plan_id: str,
        error_message: str,
    ) -> MusicPlan:
        plan = self.get_by_id(plan_id)

        if plan is None:
            raise ValueError("Music plan not found")

        plan.status = MusicStatus.FAILED
        plan.metadata_json = error_message

        self.db.commit()
        self.db.refresh(plan)

        return plan

    def delete_by_production(
        self,
        production_id: str,
    ) -> bool:
        plan = self.get_latest_by_production(production_id)

        if plan is None:
            return False

        self.db.delete(plan)
        self.db.commit()

        return True