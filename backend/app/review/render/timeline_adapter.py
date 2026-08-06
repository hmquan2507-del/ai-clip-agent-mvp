from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.db.enums import AssetType, TimelineClipType, TimelineTrackType
from app.db.models.production_asset import ProductionAsset
from app.repositories.timeline_repository import TimelineRepository
from app.timeline.compiler.factory import build_timeline_compiler_runtime
from app.timeline.compiler.models import ExecutionTimeline
from app.timeline.compiler.source import TimelineSourceMedia
from app.timeline.finalizer.models import (
    FinalTimeline,
    FinalTimelineClip,
    FinalTimelineTrack,
)

UPLOAD_BASE_PATH = Path("data/uploads")

# The persisted Timeline/TimelineTrack/TimelineClip vocabulary (app/db/enums.py)
# is not the same vocabulary TimelineCompilerRuntime/FinalTimeline expects
# (app/timeline/finalizer/models.py, app/timeline/compiler/runtime.py) - map
# to the closest concept rather than widen either side for this bridge.
_TRACK_TYPE_TO_FINAL = {
    TimelineTrackType.VIDEO: "video_primary",
    TimelineTrackType.BROLL: "broll",
    TimelineTrackType.SUBTITLE: "subtitle",
    TimelineTrackType.MUSIC: "music",
    TimelineTrackType.SOUND_EFFECT: "sfx",
    TimelineTrackType.AUDIO: "sfx",
}


class TimelineAdapterError(RuntimeError):
    """Raised when a production has no persisted timeline or source video
    to build a real ExecutionTimeline from."""


def _resolve_asset_path(asset: ProductionAsset) -> str:
    return str((UPLOAD_BASE_PATH / asset.storage_path).resolve())


def _get_source_video_asset(
    db: Session, production_id: str
) -> ProductionAsset | None:
    return (
        db.query(ProductionAsset)
        .filter(
            ProductionAsset.production_id == production_id,
            ProductionAsset.type == AssetType.SOURCE_VIDEO,
        )
        .order_by(ProductionAsset.created_at.desc())
        .first()
    )


def _get_asset_by_id(
    db: Session, asset_id: str | None
) -> ProductionAsset | None:
    if not asset_id:
        return None

    return (
        db.query(ProductionAsset)
        .filter(ProductionAsset.id == asset_id)
        .first()
    )


def _str_or_none(value: object) -> str | None:
    return None if value is None else str(value)


def build_execution_timeline_for_production(
    db: Session,
    production_id: str,
) -> ExecutionTimeline:
    """Bridge the Review Workspace's persisted DB timeline into the real
    render pipeline's ExecutionTimeline contract.

    This intentionally bypasses the AI content-graph pipeline (semantic
    analysis / broll placement / etc.) entirely - the Review Workspace's
    edited timeline is the operator's real intent and is a more direct,
    already-final source of truth than re-deriving one from AI analysis.
    """
    timeline_repository = TimelineRepository(db)
    timeline = timeline_repository.get_latest_by_production(production_id)

    if timeline is None or not timeline.tracks:
        raise TimelineAdapterError(
            "No edited timeline found for this production. "
            "Open the Review Workspace and make at least one edit "
            "before rendering."
        )

    source_asset = _get_source_video_asset(db, production_id)

    if source_asset is None:
        raise TimelineAdapterError(
            "No uploaded source video found for this production."
        )

    source_media = TimelineSourceMedia(
        asset_id=_str_or_none(source_asset.id),
        local_path=_resolve_asset_path(source_asset),
    )

    final_tracks: list[FinalTimelineTrack] = []
    primary_video_segment_index = 0

    for track in timeline.tracks:
        final_track_type = _TRACK_TYPE_TO_FINAL.get(
            track.type, "video_primary"
        )

        final_clips: list[FinalTimelineClip] = []

        for clip in track.clips:
            # A clip either points at an uploaded ProductionAsset
            # (asset_id) or carries its own local_path directly - e.g. a
            # stock b-roll/music/SFX library file the auto-edit pipeline
            # picked, which was never uploaded and has no ProductionAsset
            # row at all.
            if clip.local_path:
                local_path = clip.local_path
            else:
                clip_asset = _get_asset_by_id(db, clip.asset_id)
                local_path = (
                    _resolve_asset_path(clip_asset)
                    if clip_asset is not None
                    else None
                )

            clip_metadata = (
                json.loads(clip.metadata_json)
                if clip.metadata_json
                else {}
            )

            if final_track_type == "video_primary":
                # app/render/ffmpeg/filtergraph/builder.py's
                # _is_primary_video() hard-codes this exact
                # "clip_instruction_seg_..._source" naming convention
                # (from the AI content-graph pipeline this render engine
                # was originally built for) to pick out the primary video
                # stream from every other instruction. Match it here so
                # the existing, working filtergraph builder recognizes
                # our clip as the primary video without modifying it.
                clip_metadata["source_clip_id"] = _str_or_none(clip.id)
                clip_id = f"seg_{primary_video_segment_index}_source"
                primary_video_segment_index += 1
            else:
                clip_id = _str_or_none(clip.id)

            final_clips.append(
                FinalTimelineClip(
                    clip_id=clip_id,
                    track_type=final_track_type,
                    start_time=clip.timeline_start,
                    end_time=clip.timeline_end,
                    layer=max(1, track.position + 1),
                    asset_id=_str_or_none(clip.asset_id),
                    local_path=local_path,
                    content=clip.text,
                    metadata=clip_metadata,
                )
            )

        if not final_clips:
            continue

        final_tracks.append(
            FinalTimelineTrack(
                track_id=_str_or_none(track.id),
                track_type=final_track_type,
                layer=max(1, track.position + 1),
                clips=final_clips,
                metadata={"source_track_name": track.name},
            )
        )

    final_timeline = FinalTimeline(
        production_id=str(timeline.production_id),
        version="review-workspace-1.0",
        duration=timeline.duration_seconds,
        width=1080,
        height=1920,
        fps=30.0,
        tracks=final_tracks,
        effects=[],
        transitions=[],
        metadata={"source": "review_workspace_timeline"},
    )

    execution_timeline = build_timeline_compiler_runtime().compile(
        timeline=final_timeline,
        source_media=source_media,
    )

    blocking_issues = [
        issue
        for issue in execution_timeline.issues
        if issue.level == "error"
    ]

    if blocking_issues:
        raise TimelineAdapterError(
            "Timeline could not be compiled for render: "
            + "; ".join(issue.message for issue in blocking_issues)
        )

    return execution_timeline
