from __future__ import annotations

from sqlalchemy.orm import Session

from app.artifacts.keys import VIDEO_TRACK
from app.editing.track.video.video_track_composer import VideoTrackComposer
from app.services.base_track_composer_service import BaseTrackComposerService


class VideoTrackComposerService(BaseTrackComposerService):
    METADATA_KEY = VIDEO_TRACK
    TRACK_KEY = "video"

    def __init__(self, db: Session):
        super().__init__(
            db=db,
            composer=VideoTrackComposer(),
        )