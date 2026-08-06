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

    def replace_tracks(
        self,
        timeline_id: str,
        tracks_payload: list[dict],
    ) -> Timeline:
        """Replace every track/clip under a timeline in one transaction.

        Used to write-through the Review Workspace's authoritative editable
        timeline snapshot after every successful edit command, so the DB
        timeline a server restart or a render job reads never drifts from
        the in-memory session the operator is actually editing.
        """
        timeline = self.get_by_id(timeline_id)
        if timeline is None:
            raise ValueError("Timeline not found")

        for track in list(timeline.tracks):
            self.db.delete(track)
        self.db.flush()

        for track_payload in tracks_payload:
            track = TimelineTrack(
                timeline_id=timeline_id,
                type=track_payload["type"],
                name=track_payload["name"],
                position=track_payload["position"],
                metadata_json=track_payload.get("metadata_json"),
            )
            self.db.add(track)
            self.db.flush()

            for clip_payload in track_payload["clips"]:
                self.db.add(
                    TimelineClip(
                        track_id=track.id,
                        type=clip_payload["type"],
                        timeline_start=clip_payload["timeline_start"],
                        timeline_end=clip_payload["timeline_end"],
                        source_start=clip_payload.get("source_start"),
                        source_end=clip_payload.get("source_end"),
                        asset_id=clip_payload.get("asset_id"),
                        text=clip_payload.get("text"),
                        metadata_json=clip_payload.get("metadata_json"),
                    )
                )

        self.db.commit()
        self.db.refresh(timeline)

        return timeline

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