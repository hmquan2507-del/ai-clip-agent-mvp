from __future__ import annotations

from sqlalchemy.orm import Session, selectinload

from app.db.enums import SubtitleStatus, SubtitleStyle
from app.db.models.subtitle import Subtitle, SubtitleCue


class SubtitleRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_subtitle(
        self,
        production_id: str,
        timeline_id: str | None = None,
        style: SubtitleStyle = SubtitleStyle.DEFAULT,
        language: str | None = None,
    ) -> Subtitle:
        subtitle = Subtitle(
            production_id=production_id,
            timeline_id=timeline_id,
            status=SubtitleStatus.PROCESSING,
            style=style,
            language=language,
        )

        self.db.add(subtitle)
        self.db.commit()
        self.db.refresh(subtitle)

        return subtitle

    def get_by_id(self, subtitle_id: str) -> Subtitle | None:
        return (
            self.db.query(Subtitle)
            .options(selectinload(Subtitle.cues))
            .filter(Subtitle.id == subtitle_id)
            .first()
        )

    def get_latest_by_production(self, production_id: str) -> Subtitle | None:
        return (
            self.db.query(Subtitle)
            .options(selectinload(Subtitle.cues))
            .filter(Subtitle.production_id == production_id)
            .order_by(Subtitle.created_at.desc())
            .first()
        )

    def add_cue(
        self,
        subtitle_id: str,
        start_time: float,
        end_time: float,
        text: str,
        style_json: str | None = None,
    ) -> SubtitleCue:
        cue = SubtitleCue(
            subtitle_id=subtitle_id,
            start_time=start_time,
            end_time=end_time,
            text=text,
            style_json=style_json,
        )

        self.db.add(cue)
        self.db.commit()
        self.db.refresh(cue)

        return cue

    def mark_completed(
        self,
        subtitle_id: str,
        metadata_json: str | None = None,
    ) -> Subtitle:
        subtitle = self.get_by_id(subtitle_id)
        if subtitle is None:
            raise ValueError("Subtitle not found")

        subtitle.status = SubtitleStatus.COMPLETED
        subtitle.metadata_json = metadata_json

        self.db.commit()
        self.db.refresh(subtitle)

        return subtitle

    def mark_failed(
        self,
        subtitle_id: str,
        error_message: str,
    ) -> Subtitle:
        subtitle = self.get_by_id(subtitle_id)
        if subtitle is None:
            raise ValueError("Subtitle not found")

        subtitle.status = SubtitleStatus.FAILED
        subtitle.metadata_json = error_message

        self.db.commit()
        self.db.refresh(subtitle)

        return subtitle

    def delete_by_production(self, production_id: str) -> bool:
        subtitle = self.get_latest_by_production(production_id)

        if subtitle is None:
            return False

        self.db.delete(subtitle)
        self.db.commit()

        return True