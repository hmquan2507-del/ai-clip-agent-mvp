from __future__ import annotations

from sqlalchemy.orm import Session, selectinload

from app.db.enums import RenderAssetType, RenderPlanStatus, RenderTrackType
from app.db.models.render_plan import RenderAsset, RenderPlan, RenderTrack


class RenderRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_plan(
        self,
        production_id: str,
        timeline_id: str | None = None,
        resolution: str = "1080x1920",
        fps: int = 30,
    ) -> RenderPlan:
        plan = RenderPlan(
            production_id=production_id,
            timeline_id=timeline_id,
            status=RenderPlanStatus.PROCESSING,
            duration_seconds=0,
            resolution=resolution,
            fps=fps,
        )

        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)

        return plan

    def get_by_id(self, plan_id: str) -> RenderPlan | None:
        return (
            self.db.query(RenderPlan)
            .options(
                selectinload(RenderPlan.tracks).selectinload(RenderTrack.assets)
            )
            .filter(RenderPlan.id == plan_id)
            .first()
        )

    def get_latest_by_production(
        self,
        production_id: str,
    ) -> RenderPlan | None:
        return (
            self.db.query(RenderPlan)
            .options(
                selectinload(RenderPlan.tracks).selectinload(RenderTrack.assets)
            )
            .filter(RenderPlan.production_id == production_id)
            .order_by(RenderPlan.created_at.desc())
            .first()
        )

    def add_track(
        self,
        render_plan_id: str,
        track_type: RenderTrackType,
        name: str,
        position: int = 0,
        metadata_json: str | None = None,
    ) -> RenderTrack:
        track = RenderTrack(
            render_plan_id=render_plan_id,
            type=track_type,
            name=name,
            position=position,
            metadata_json=metadata_json,
        )

        self.db.add(track)
        self.db.commit()
        self.db.refresh(track)

        return track

    def add_asset(
        self,
        render_track_id: str,
        asset_type: RenderAssetType,
        start_time: float,
        end_time: float,
        asset_id: str | None = None,
        source_start: float | None = None,
        source_end: float | None = None,
        text: str | None = None,
        prompt: str | None = None,
        metadata_json: str | None = None,
    ) -> RenderAsset:
        asset = RenderAsset(
            render_track_id=render_track_id,
            asset_id=asset_id,
            type=asset_type,
            start_time=start_time,
            end_time=end_time,
            source_start=source_start,
            source_end=source_end,
            text=text,
            prompt=prompt,
            metadata_json=metadata_json,
        )

        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)

        return asset

    def mark_completed(
        self,
        plan_id: str,
        duration_seconds: float,
        metadata_json: str | None = None,
    ) -> RenderPlan:
        plan = self.get_by_id(plan_id)

        if plan is None:
            raise ValueError("Render plan not found")

        plan.status = RenderPlanStatus.COMPLETED
        plan.duration_seconds = duration_seconds
        plan.metadata_json = metadata_json

        self.db.commit()
        self.db.refresh(plan)

        return plan

    def mark_failed(
        self,
        plan_id: str,
        error_message: str,
    ) -> RenderPlan:
        plan = self.get_by_id(plan_id)

        if plan is None:
            raise ValueError("Render plan not found")

        plan.status = RenderPlanStatus.FAILED
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