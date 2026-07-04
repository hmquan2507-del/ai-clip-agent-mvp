from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.enums import SubtitleStyle
from app.repositories.production_repository import ProductionRepository
from app.repositories.subtitle_repository import SubtitleRepository
from app.repositories.timeline_repository import TimelineRepository
from app.services.subtitle_engine import SubtitleEngine


class SubtitleService:
    def __init__(self, db: Session):
        self.db = db

        self.production_repo = ProductionRepository(db)
        self.timeline_repo = TimelineRepository(db)
        self.subtitle_repo = SubtitleRepository(db)

        self.subtitle_engine = SubtitleEngine()

    def generate_subtitle(
        self,
        production_id: UUID,
        style: SubtitleStyle = SubtitleStyle.DEFAULT,
    ):
        production = self.production_repo.get_by_id(production_id)

        if production is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Production not found",
            )

        timeline = self.timeline_repo.get_latest_by_production(
            str(production_id),
        )

        if timeline is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Timeline not found",
            )

        subtitle = self.subtitle_repo.create_subtitle(
            production_id=str(production_id),
            timeline_id=timeline.id,
            style=style,
            language="vi",
        )

        try:
            result = self.subtitle_engine.build_from_timeline(
                timeline=timeline,
                style=style,
            )

            for cue in result["cues"]:
                self.subtitle_repo.add_cue(
                    subtitle_id=subtitle.id,
                    start_time=cue["start_time"],
                    end_time=cue["end_time"],
                    text=cue["text"],
                    style_json=cue["style_json"],
                )

            return self.subtitle_repo.mark_completed(
                subtitle.id,
            )

        except Exception as exc:
            self.subtitle_repo.mark_failed(
                subtitle.id,
                str(exc),
            )
            raise

    def get_latest_subtitle(
        self,
        production_id: UUID,
    ):
        subtitle = self.subtitle_repo.get_latest_by_production(
            str(production_id),
        )

        if subtitle is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subtitle not found",
            )

        return subtitle

    def delete_latest_subtitle(
        self,
        production_id: UUID,
    ):
        deleted = self.subtitle_repo.delete_by_production(
            str(production_id),
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subtitle not found",
            )

        return True