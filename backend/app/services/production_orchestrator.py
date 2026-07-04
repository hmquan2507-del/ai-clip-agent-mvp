from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.db.enums import MusicMood
from app.services.broll_service import BrollService
from app.services.editing_service import EditingService
from app.services.music_service import MusicService
from app.services.render_service import RenderService
from app.services.sound_effect_service import SoundEffectService
from app.services.subtitle_service import SubtitleService
from app.services.timeline_service import TimelineService


class ProductionOrchestrator:
    def __init__(self, db: Session):
        self.db = db

    async def run_demo_pipeline(
        self,
        production_id: UUID,
    ) -> dict:
        editing_plan = await EditingService(self.db).generate_editing_plan(
            production_id=production_id,
            provider="mock",
            target_duration_seconds=60,
        )

        timeline = TimelineService(self.db).generate_timeline(
            production_id=production_id,
        )

        subtitle = SubtitleService(self.db).generate_subtitle(
            production_id=production_id,
        )

        broll = BrollService(self.db).generate_broll_plan(
            production_id=production_id,
        )

        sound_effect = SoundEffectService(self.db).generate_sound_effect_plan(
            production_id=production_id,
        )

        music = MusicService(self.db).generate_music_plan(
            production_id=production_id,
            mood=MusicMood.ENERGETIC,
        )

        render_plan = RenderService(self.db).generate_render_plan(
            production_id=production_id,
        )

        return {
            "editing_plan_id": str(editing_plan.id),
            "timeline_id": str(timeline.id),
            "subtitle_id": str(subtitle.id),
            "broll_plan_id": str(broll.id),
            "sound_effect_plan_id": str(sound_effect.id),
            "music_plan_id": str(music.id),
            "render_plan_id": str(render_plan.id),
        }