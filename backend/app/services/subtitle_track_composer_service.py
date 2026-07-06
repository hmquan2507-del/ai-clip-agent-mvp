from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.artifacts.keys import SUBTITLE_TRACK
from app.editing.track.subtitle.subtitle_track_composer import SubtitleTrackComposer
from app.services.base_track_composer_service import BaseTrackComposerService


class SubtitleTrackComposerService(BaseTrackComposerService):
    METADATA_KEY = SUBTITLE_TRACK
    TRACK_KEY = "subtitle"

    def __init__(self, db: Session):
        super().__init__(
            db=db,
            composer=SubtitleTrackComposer(),
        )

    def build_kwargs(
        self,
        graph: Any,
    ) -> dict[str, Any]:
        return {
            "segments": self.segment_loader.build_segments(graph),
        }