from __future__ import annotations

from sqlalchemy.orm import Session, selectinload

from app.db.enums import TimelineStatus
from app.db.models.timeline import Timeline, TimelineClip, TimelineTrack


class TimelineRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_timeline(
        self,
        production_id: str,
        editing_plan_id: str | None = None,
    ) -> Timeline:
        timeline = Timeline(
            production_id=production_id,
            editing_plan_id=editing_plan_id,
            status=TimelineStatus.PROCESSING,
            duration_seconds=0,
            version=1,
        )

        self.db.add(timeline)
        self.db.commit()
        self.db.refresh(timeline)

        return timeline

    def get_by_id(self, timeline_id: str) -> Timeline | None:
        return (
            self.db.query(Timeline)
            .options(
                selectinload(Timeline.tracks).selectinload(TimelineTrack.clips)
            )
            .filter(Timeline.id == timeline_id)
            .first()
        )

    def get_latest_by_production(self, production_id: str) -> Timeline | None:
        return (
            self.db.query(Timeline)
            .options(
                selectinload(Timeline.tracks).selectinload(TimelineTrack.clips)
            )
            .filter(Timeline.production_id == production_id)
            .order_by(Timeline.created_at.desc())
            .first()
        )

    def add_track(
        self,
        timeline_id: str,
        track_type,
        name: str,
        position: int = 0,
        metadata_json: str | None = None,
    ) -> TimelineTrack:
        track = TimelineTrack(
            timeline_id=timeline_id,
            type=track_type,
            name=name,
            position=position,
            metadata_json=metadata_json,
        )

        self.db.add(track)
        self.db.commit()
        self.db.refresh(track)

        return track

    def add_clip(
        self,
        track_id: str,
        clip_type,
        timeline_start: float,
        timeline_end: float,
        source_start: float | None = None,
        source_end: float | None = None,
        asset_id: str | None = None,
        text: str | None = None,
        metadata_json: str | None = None,
    ) -> TimelineClip:
        clip = TimelineClip(
            track_id=track_id,
            type=clip_type,
            timeline_start=timeline_start,
            timeline_end=timeline_end,
            source_start=source_start,
            source_end=source_end,
            asset_id=asset_id,
            text=text,
            metadata_json=metadata_json,
        )

        self.db.add(clip)
        self.db.commit()
        self.db.refresh(clip)

        return clip

    def mark_completed(
        self,
        timeline_id: str,
        duration_seconds: float,
    ) -> Timeline:
        timeline = self.get_by_id(timeline_id)
        if timeline is None:
            raise ValueError("Timeline not found")

        timeline.status = TimelineStatus.COMPLETED
        timeline.duration_seconds = duration_seconds

        self.db.commit()
        self.db.refresh(timeline)

        return timeline

    def mark_failed(
        self,
        timeline_id: str,
        error_message: str,
    ) -> Timeline:
        timeline = self.get_by_id(timeline_id)
        if timeline is None:
            raise ValueError("Timeline not found")

        timeline.status = TimelineStatus.FAILED
        timeline.metadata_json = error_message

        self.db.commit()
        self.db.refresh(timeline)

        return timeline

    def delete_by_production(self, production_id: str) -> bool:
        timeline = self.get_latest_by_production(production_id)
        if timeline is None:
            return False

        self.db.delete(timeline)
        self.db.commit()

        return True