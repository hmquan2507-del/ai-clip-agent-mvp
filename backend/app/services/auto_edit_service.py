from __future__ import annotations

import logging
from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.enums import AssetType
from app.db.models.production_asset import ProductionAsset
from app.media.validation.factory import build_media_validation_runtime
from app.review.editing.enums import EditableClipType, EditableTrackType
from app.review.editing.models import (
    EditableTimeline,
    EditableTimelineClip,
    EditableTimelineTrack,
)
from app.review.persistence import sync_editable_timeline_to_db
from app.services.gemini_transcription_service import (
    GeminiTranscriptionError,
    transcribe_video,
)

logger = logging.getLogger(__name__)

UPLOAD_BASE_PATH = Path("data/uploads")

BROLL_LIBRARY_PATHS = [
    Path("storage/assets/broll/pexels"),
    Path("storage/assets/broll/pixabay"),
]
MUSIC_LIBRARY_PATH = Path("storage/assets/music/internal_music")
SOUND_EFFECT_LIBRARY_PATH = Path("storage/assets/sound_effect/freesound")

BROLL_PLACEMENT_DURATION_SECONDS = 3.0
BROLL_MIN_GAP_SECONDS = 6.0
MUSIC_VOLUME = 0.2


class AutoEditError(RuntimeError):
    pass


def _list_real_media_files(directory: Path) -> list[tuple[Path, float]]:
    """ffprobe every file in a stock library directory and keep only the
    ones that are actually valid, playable media - some of this repo's
    "stock" fixtures turned out to be placeholder text files with a media
    extension (e.g. a 15-byte corporate_background_music.mp3 containing
    the literal text "demo music file")."""
    validator = build_media_validation_runtime()
    results: list[tuple[Path, float]] = []

    if not directory.exists():
        return results

    for path in sorted(directory.glob("*")):
        if not path.is_file():
            continue

        analysis = validator.validate(str(path), require_video=False)

        if not analysis.valid or not analysis.duration:
            logger.warning(
                "Skipping invalid stock asset %s: %s",
                path,
                analysis.errors,
            )
            continue

        results.append((path, analysis.duration))

    return results


def _build_broll_track(
    video_duration: float,
) -> EditableTimelineTrack | None:
    broll_files = [
        item
        for directory in BROLL_LIBRARY_PATHS
        for item in _list_real_media_files(directory)
    ]

    if not broll_files:
        return None

    clips: list[EditableTimelineClip] = []
    cursor = BROLL_MIN_GAP_SECONDS
    index = 0

    while cursor + 1.0 < video_duration:
        path, file_duration = broll_files[index % len(broll_files)]
        placement_duration = min(
            BROLL_PLACEMENT_DURATION_SECONDS,
            file_duration,
            video_duration - cursor,
        )

        if placement_duration >= 1.0:
            clips.append(
                EditableTimelineClip(
                    clip_id=f"clip_broll_{index}",
                    track_id="track_broll",
                    clip_type=EditableClipType.BROLL,
                    start_time=cursor,
                    end_time=cursor + placement_duration,
                    source_start=0.0,
                    source_end=placement_duration,
                    local_path=str(path.resolve()),
                    metadata={"source_filename": path.name},
                )
            )
            cursor += placement_duration + BROLL_MIN_GAP_SECONDS
        else:
            cursor += BROLL_MIN_GAP_SECONDS

        index += 1

    if not clips:
        return None

    return EditableTimelineTrack(
        track_id="track_broll",
        track_type=EditableTrackType.BROLL,
        name="B-roll",
        position=2,
        clips=clips,
    )


def _build_music_track(video_duration: float) -> EditableTimelineTrack | None:
    music_files = _list_real_media_files(MUSIC_LIBRARY_PATH)

    if not music_files:
        return None

    music_path, music_duration = music_files[0]
    music_span = min(video_duration, music_duration)

    return EditableTimelineTrack(
        track_id="track_music",
        track_type=EditableTrackType.MUSIC,
        name="Nhạc nền",
        position=3,
        clips=[
            EditableTimelineClip(
                clip_id="clip_music",
                track_id="track_music",
                clip_type=EditableClipType.MUSIC,
                start_time=0.0,
                end_time=music_span,
                source_start=0.0,
                source_end=music_span,
                local_path=str(music_path.resolve()),
                volume=MUSIC_VOLUME,
                metadata={"source_filename": music_path.name},
            ),
        ],
    )


def _build_sound_effect_track(
    video_duration: float,
) -> EditableTimelineTrack | None:
    sfx_files = _list_real_media_files(SOUND_EFFECT_LIBRARY_PATH)

    if not sfx_files:
        return None

    sfx_path, sfx_duration = sfx_files[0]
    sfx_span = min(sfx_duration, video_duration)

    return EditableTimelineTrack(
        track_id="track_sfx",
        track_type=EditableTrackType.SOUND_EFFECT,
        name="Hiệu ứng âm thanh",
        position=4,
        clips=[
            EditableTimelineClip(
                clip_id="clip_sfx_hook",
                track_id="track_sfx",
                clip_type=EditableClipType.SOUND_EFFECT,
                start_time=0.0,
                end_time=sfx_span,
                source_start=0.0,
                source_end=sfx_span,
                local_path=str(sfx_path.resolve()),
                metadata={"source_filename": sfx_path.name},
            ),
        ],
    )


def run_auto_edit(
    db: Session,
    production_id: UUID | str,
) -> EditableTimeline:
    """Automatically build a first-pass edited timeline for a freshly
    uploaded production: real transcript-based subtitles, b-roll picked
    from the real stock library, one background-music bed, and one hook
    sound effect - then persist it exactly like a manual edit would be
    (via sync_editable_timeline_to_db), so the operator lands on the
    Review Workspace with a real, editable, renderable timeline already
    in place.
    """
    normalized_id = str(production_id)

    source_asset = (
        db.query(ProductionAsset)
        .filter(
            ProductionAsset.production_id == normalized_id,
            ProductionAsset.type == AssetType.SOURCE_VIDEO,
        )
        .order_by(ProductionAsset.created_at.desc())
        .first()
    )

    if source_asset is None:
        raise AutoEditError(
            "No uploaded source video found for this production."
        )

    video_duration = float(source_asset.duration or 0.0)

    if video_duration <= 0:
        raise AutoEditError(
            "Source video has no known duration; cannot auto-edit."
        )

    source_local_path = str(
        (UPLOAD_BASE_PATH / source_asset.storage_path).resolve()
    )

    try:
        segments = transcribe_video(source_local_path)
    except GeminiTranscriptionError as error:
        raise AutoEditError(f"Transcription failed: {error}") from error

    tracks: list[EditableTimelineTrack] = [
        EditableTimelineTrack(
            track_id="track_video",
            track_type=EditableTrackType.VIDEO_PRIMARY,
            name="Video chính",
            position=0,
            clips=[
                EditableTimelineClip(
                    clip_id="clip_source_video",
                    track_id="track_video",
                    clip_type=EditableClipType.VIDEO,
                    start_time=0.0,
                    end_time=video_duration,
                    source_start=0.0,
                    source_end=video_duration,
                    asset_id=str(source_asset.id),
                ),
            ],
        )
    ]

    subtitle_clips = [
        EditableTimelineClip(
            clip_id=f"clip_subtitle_{index}",
            track_id="track_subtitle",
            clip_type=EditableClipType.SUBTITLE,
            start_time=segment.start_seconds,
            end_time=min(segment.end_seconds, video_duration),
            text=segment.text,
        )
        for index, segment in enumerate(segments)
        if segment.start_seconds < video_duration
    ]

    if subtitle_clips:
        tracks.append(
            EditableTimelineTrack(
                track_id="track_subtitle",
                track_type=EditableTrackType.SUBTITLE,
                name="Phụ đề",
                position=1,
                clips=subtitle_clips,
            )
        )

    broll_track = _build_broll_track(video_duration)
    if broll_track is not None:
        tracks.append(broll_track)

    music_track = _build_music_track(video_duration)
    if music_track is not None:
        tracks.append(music_track)

    sfx_track = _build_sound_effect_track(video_duration)
    if sfx_track is not None:
        tracks.append(sfx_track)

    timeline = EditableTimeline(
        production_id=normalized_id,
        tracks=tracks,
        duration=video_duration,
    )

    sync_editable_timeline_to_db(db, timeline)

    return timeline
