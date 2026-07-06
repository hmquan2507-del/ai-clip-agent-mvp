from __future__ import annotations

from sqlalchemy.orm import Session

from app.artifacts.keys import AUDIO_TRACK
from app.editing.track.audio.audio_track_composer import AudioTrackComposer
from app.services.base_track_composer_service import BaseTrackComposerService


class AudioTrackComposerService(BaseTrackComposerService):
    METADATA_KEY = AUDIO_TRACK
    TRACK_KEY = "audio"

    def __init__(self, db: Session):
        super().__init__(
            db=db,
            composer=AudioTrackComposer(),
        )