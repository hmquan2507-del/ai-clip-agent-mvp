from __future__ import annotations

from typing import Any

from app.review.editing.enums import (
    EditableClipType,
    EditableTrackType,
    TimelineOverlapPolicy,
)
from app.review.editing.models import (
    EditableTimeline,
    EditableTimelineClip,
    EditableTimelineTrack,
)


def build_editable_timeline(
    *,
    production_id: str,
    tracks: list[Any],
    duration: float = 0.0,
    fps: float = 30.0,
    width: int | None = None,
    height: int | None = None,
    version: str = "16.1.4",
) -> EditableTimeline:
    editable_tracks: list[
        EditableTimelineTrack
    ] = []

    for track_index, raw_track in enumerate(
        tracks
    ):
        track_id = str(
            _read(
                raw_track,
                "track_id",
                _read(
                    raw_track,
                    "id",
                    f"track_{track_index}",
                ),
            )
        )

        track_type = _track_type(
            _read(
                raw_track,
                "track_type",
                _read(
                    raw_track,
                    "type",
                    "unknown",
                ),
            )
        )

        overlap_policy = (
            _default_overlap_policy(
                track_type
            )
        )

        clips: list[
            EditableTimelineClip
        ] = []

        for clip_index, raw_clip in enumerate(
            _read(
                raw_track,
                "clips",
                [],
            )
            or []
        ):
            clip_id = str(
                _read(
                    raw_clip,
                    "clip_id",
                    _read(
                        raw_clip,
                        "id",
                        (
                            f"{track_id}_"
                            f"clip_{clip_index}"
                        ),
                    ),
                )
            )

            start_time = float(
                _read(
                    raw_clip,
                    "start_time",
                    _read(
                        raw_clip,
                        "timeline_start",
                        0.0,
                    ),
                )
                or 0.0
            )

            raw_end_time = _read(
                raw_clip,
                "end_time",
                _read(
                    raw_clip,
                    "timeline_end",
                    None,
                ),
            )

            if raw_end_time is None:
                clip_duration = float(
                    _read(
                        raw_clip,
                        "duration",
                        0.0,
                    )
                    or 0.0
                )

                end_time = (
                    start_time
                    + clip_duration
                )
            else:
                end_time = float(
                    raw_end_time
                )

            clips.append(
                EditableTimelineClip(
                    clip_id=clip_id,
                    track_id=track_id,
                    clip_type=_clip_type(
                        _read(
                            raw_clip,
                            "clip_type",
                            _read(
                                raw_clip,
                                "type",
                                _infer_clip_type(
                                    track_type
                                ),
                            ),
                        )
                    ),
                    start_time=start_time,
                    end_time=end_time,
                    source_start=_optional_float(
                        _read(
                            raw_clip,
                            "source_start",
                        )
                    ),
                    source_end=_optional_float(
                        _read(
                            raw_clip,
                            "source_end",
                        )
                    ),
                    source_duration=(
                        _optional_float(
                            _read(
                                raw_clip,
                                "source_duration",
                            )
                        )
                    ),
                    asset_id=_optional_string(
                        _read(
                            raw_clip,
                            "asset_id",
                        )
                    ),
                    local_path=_read(
                        raw_clip,
                        "local_path",
                    ),
                    text=_read(
                        raw_clip,
                        "text",
                        _read(
                            raw_clip,
                            "content",
                        ),
                    ),
                    volume=_optional_float(
                        _read(
                            raw_clip,
                            "volume",
                        )
                    ),
                    opacity=_optional_float(
                        _read(
                            raw_clip,
                            "opacity",
                        )
                    ),
                    speed=_optional_float(
                        _read(
                            raw_clip,
                            "speed",
                        )
                    ),
                    enabled=bool(
                        _read(
                            raw_clip,
                            "enabled",
                            True,
                        )
                    ),
                    metadata=dict(
                        _read(
                            raw_clip,
                            "metadata",
                            {},
                        )
                        or {}
                    ),
                )
            )

        editable_tracks.append(
            EditableTimelineTrack(
                track_id=track_id,
                track_type=track_type,
                name=_read(
                    raw_track,
                    "name",
                ),
                position=int(
                    _read(
                        raw_track,
                        "position",
                        track_index,
                    )
                    or 0
                ),
                layer=int(
                    _read(
                        raw_track,
                        "layer",
                        track_index,
                    )
                    or 0
                ),
                locked=bool(
                    _read(
                        raw_track,
                        "locked",
                        False,
                    )
                ),
                muted=bool(
                    _read(
                        raw_track,
                        "muted",
                        False,
                    )
                ),
                hidden=bool(
                    _read(
                        raw_track,
                        "hidden",
                        False,
                    )
                ),
                enabled=bool(
                    _read(
                        raw_track,
                        "enabled",
                        True,
                    )
                ),
                overlap_policy=overlap_policy,
                clips=clips,
                metadata=dict(
                    _read(
                        raw_track,
                        "metadata",
                        {},
                    )
                    or {}
                ),
            )
        )

    return EditableTimeline(
        production_id=production_id,
        version=version,
        duration=duration,
        fps=fps,
        width=width,
        height=height,
        tracks=editable_tracks,
        metadata={
            "factory": (
                "build_editable_timeline"
            ),
        },
    )


def build_editable_timeline_from_workspace(
    workspace: Any,
) -> EditableTimeline:
    production = _read(
        workspace,
        "production",
        {},
    )
    timeline = _read(
        workspace,
        "timeline",
        {},
    )
    canvas = _read(
        timeline,
        "canvas",
        {},
    )

    production_id = str(
        _read(
            production,
            "production_id",
            "",
        )
    )

    if not production_id:
        raise ValueError(
            "Workspace does not contain "
            "production_id."
        )

    return build_editable_timeline(
        production_id=production_id,
        tracks=list(
            _read(
                timeline,
                "tracks",
                [],
            )
            or []
        ),
        duration=float(
            _read(
                timeline,
                "duration",
                0.0,
            )
            or 0.0
        ),
        fps=float(
            _read(
                canvas,
                "fps",
                _read(
                    timeline,
                    "fps",
                    30.0,
                ),
            )
            or 30.0
        ),
        width=_optional_int(
            _read(
                canvas,
                "width",
            )
        ),
        height=_optional_int(
            _read(
                canvas,
                "height",
            )
        ),
    )


def _default_overlap_policy(
    track_type: EditableTrackType,
) -> TimelineOverlapPolicy:
    if track_type in {
        EditableTrackType.VIDEO_PRIMARY,
    }:
        return TimelineOverlapPolicy.FORBID

    return TimelineOverlapPolicy.ALLOW


def _infer_clip_type(
    track_type: EditableTrackType,
) -> str:
    mapping = {
        EditableTrackType.VIDEO_PRIMARY: (
            EditableClipType.VIDEO.value
        ),
        EditableTrackType.VIDEO_OVERLAY: (
            EditableClipType.VIDEO.value
        ),
        EditableTrackType.BROLL: (
            EditableClipType.BROLL.value
        ),
        EditableTrackType.SUBTITLE: (
            EditableClipType.SUBTITLE.value
        ),
        EditableTrackType.MUSIC: (
            EditableClipType.MUSIC.value
        ),
        EditableTrackType.SOUND_EFFECT: (
            EditableClipType
            .SOUND_EFFECT.value
        ),
        EditableTrackType.VOICE: (
            EditableClipType.VOICE.value
        ),
        EditableTrackType.AUDIO: (
            EditableClipType.AUDIO.value
        ),
        EditableTrackType.EFFECT: (
            EditableClipType.EFFECT.value
        ),
    }

    return mapping.get(
        track_type,
        EditableClipType.UNKNOWN.value,
    )


def _track_type(
    value: Any,
) -> EditableTrackType:
    normalized = _enum_value(
        value
    )

    try:
        return EditableTrackType(
            normalized
        )
    except ValueError:
        return EditableTrackType.UNKNOWN


def _clip_type(
    value: Any,
) -> EditableClipType:
    normalized = _enum_value(
        value
    )

    aliases = {
        "video_primary": "video",
        "video_overlay": "video",
    }

    normalized = aliases.get(
        normalized,
        normalized,
    )

    try:
        return EditableClipType(
            normalized
        )
    except ValueError:
        return EditableClipType.UNKNOWN


def _enum_value(
    value: Any,
) -> str:
    if value is None:
        return "unknown"

    if hasattr(value, "value"):
        return str(value.value)

    return str(value)


def _optional_float(
    value: Any,
) -> float | None:
    if value is None:
        return None

    return float(value)


def _optional_int(
    value: Any,
) -> int | None:
    if value is None:
        return None

    return int(value)


def _optional_string(
    value: Any,
) -> str | None:
    if value is None:
        return None

    return str(value)


def _read(
    source: Any,
    key: str,
    default: Any = None,
) -> Any:
    if source is None:
        return default

    if isinstance(source, dict):
        return source.get(
            key,
            default,
        )

    return getattr(
        source,
        key,
        default,
    )