from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories.broll_repository import BrollRepository
from app.repositories.music_repository import MusicRepository
from app.repositories.production_repository import ProductionRepository
from app.repositories.render_repository import RenderRepository
from app.repositories.sound_effect_repository import SoundEffectRepository
from app.repositories.subtitle_repository import SubtitleRepository
from app.repositories.timeline_repository import TimelineRepository
from app.services.base_runtime_service import BaseRuntimeService
from app.services.render_engine import RenderEngine


class RenderService(BaseRuntimeService):
    def __init__(self, db: Session):
        super().__init__(db)

        self.production_repo = ProductionRepository(db)

        self.timeline_repo = TimelineRepository(db)
        self.subtitle_repo = SubtitleRepository(db)
        self.broll_repo = BrollRepository(db)
        self.sound_effect_repo = SoundEffectRepository(db)
        self.music_repo = MusicRepository(db)

        self.render_repo = RenderRepository(db)

        self.render_engine = RenderEngine()

    def generate_render_plan(
        self,
        production_id: UUID,
    ):
        self.ensure_production_exists(production_id)

        timeline = self.timeline_repo.get_latest_by_production(
            str(production_id)
        )

        if timeline is None:
            self.raise_missing_dependency("Timeline not found")

        subtitle = self.subtitle_repo.get_latest_by_production(
            str(production_id)
        )

        broll = self.broll_repo.get_latest_by_production(
            str(production_id)
        )

        sound_effect = self.sound_effect_repo.get_latest_by_production(
            str(production_id)
        )

        music = self.music_repo.get_latest_by_production(
            str(production_id)
        )

        result = self.render_engine.build(
            timeline=timeline,
            subtitle=subtitle,
            broll_plan=broll,
            sound_effect_plan=sound_effect,
            music_plan=music,
        )

        plan = self.render_repo.create_plan(
            production_id=str(production_id),
            timeline_id=timeline.id,
        )

        try:

            for track_data in result["tracks"]:

                track = self.render_repo.add_track(
                    render_plan_id=plan.id,
                    track_type=track_data["type"],
                    name=track_data["name"],
                    position=track_data["position"],
                )

                for asset in track_data["assets"]:

                    self.render_repo.add_asset(
                        render_track_id=track.id,
                        asset_type=asset["type"],
                        asset_id=asset.get("asset_id"),
                        start_time=asset["start_time"],
                        end_time=asset["end_time"],
                        source_start=asset.get("source_start"),
                        source_end=asset.get("source_end"),
                        text=asset.get("text"),
                        prompt=asset.get("prompt"),
                        metadata_json=self.render_engine.dumps_json(
                            asset.get("metadata")
                        ),
                    )

            return self.render_repo.mark_completed(
                plan_id=plan.id,
                duration_seconds=result["duration_seconds"],
                metadata_json=self.render_engine.dumps_json(
                    result["metadata"]
                ),
            )

        except Exception as exc:

            self.render_repo.mark_failed(
                plan_id=plan.id,
                error_message=str(exc),
            )

            raise

    def get_latest_render_plan(
        self,
        production_id: UUID,
    ):
        plan = self.render_repo.get_latest_by_production(
            str(production_id)
        )

        if plan is None:
            self.raise_not_found("Render plan not found")

        return plan

    def delete_latest_render_plan(
        self,
        production_id: UUID,
    ) -> bool:

        deleted = self.render_repo.delete_by_production(
            str(production_id)
        )

        if not deleted:
            self.raise_not_found("Render plan not found")

        return True