from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.db.enums import TimelineClipType, TimelineTrackType
from app.repositories.timeline_repository import TimelineRepository
from app.review.editing.enums import EditableClipType, EditableTrackType
from app.review.editing.models import EditableTimeline

# The Review Workspace's editable-timeline vocabulary is richer than the
# persisted Timeline's (no VOICE/AUDIO/EFFECT/UNKNOWN track type, no
# VIDEO/VOICE/AUDIO/EFFECT/UNKNOWN clip type) - map to the closest existing
# DB value rather than widen the DB enum for this write-through.
_TRACK_TYPE_TO_DB = {
    EditableTrackType.VIDEO_PRIMARY: TimelineTrackType.VIDEO,
    EditableTrackType.VIDEO_OVERLAY: TimelineTrackType.VIDEO,
    EditableTrackType.BROLL: TimelineTrackType.BROLL,
    EditableTrackType.SUBTITLE: TimelineTrackType.SUBTITLE,
    EditableTrackType.MUSIC: TimelineTrackType.MUSIC,
    EditableTrackType.SOUND_EFFECT: TimelineTrackType.SOUND_EFFECT,
    EditableTrackType.VOICE: TimelineTrackType.AUDIO,
    EditableTrackType.AUDIO: TimelineTrackType.AUDIO,
    EditableTrackType.EFFECT: TimelineTrackType.VIDEO,
    EditableTrackType.UNKNOWN: TimelineTrackType.VIDEO,
}

_CLIP_TYPE_TO_DB = {
    EditableClipType.VIDEO: TimelineClipType.SOURCE,
    EditableClipType.BROLL: TimelineClipType.BROLL,
    EditableClipType.SUBTITLE: TimelineClipType.SUBTITLE,
    EditableClipType.MUSIC: TimelineClipType.MUSIC,
    EditableClipType.SOUND_EFFECT: TimelineClipType.SOUND_EFFECT,
    EditableClipType.VOICE: TimelineClipType.GENERATED,
    EditableClipType.AUDIO: TimelineClipType.GENERATED,
    EditableClipType.EFFECT: TimelineClipType.GENERATED,
    EditableClipType.UNKNOWN: TimelineClipType.GENERATED,
}


def sync_editable_timeline_to_db(
    db: Session,
    timeline: EditableTimeline,
) -> None:
    """Write-through the Review Workspace's authoritative in-memory timeline
    into the persisted Timeline/TimelineTrack/TimelineClip rows.

    Called after every successful timeline/clipboard command so the DB
    timeline - the one render, a server restart, or any other reader sees -
    never drifts from what the operator is actually editing in the session.
    """
    repository = TimelineRepository(db)

    record = repository.get_latest_by_production(timeline.production_id)
    if record is None:
        record = repository.create_timeline(timeline.production_id)

    tracks_payload = [
        {
            "type": _TRACK_TYPE_TO_DB.get(
                track.track_type, TimelineTrackType.VIDEO
            ),
            "name": track.name or track.track_type.value,
            "position": track.position,
            "metadata_json": json.dumps(track.metadata) if track.metadata else None,
            "clips": [
                {
                    "type": _CLIP_TYPE_TO_DB.get(
                        clip.clip_type, TimelineClipType.GENERATED
                    ),
                    "timeline_start": clip.start_time,
                    "timeline_end": clip.end_time,
                    "source_start": clip.source_start,
                    "source_end": clip.source_end,
                    "asset_id": clip.asset_id,
                    "local_path": clip.local_path,
                    "text": clip.text,
                    "metadata_json": json.dumps(clip.metadata) if clip.metadata else None,
                }
                for clip in track.clips
            ],
        }
        for track in timeline.tracks
    ]

    repository.replace_tracks(record.id, tracks_payload)
    repository.mark_completed(record.id, timeline.duration)
