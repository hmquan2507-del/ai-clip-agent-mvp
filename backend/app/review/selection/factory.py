from __future__ import annotations

from typing import Any

from app.review.selection.models import (
    TimelineSelectableClip,
    TimelineSelectableTrack,
    TimelineSelectionCatalog,
)
from app.review.selection.runtime import (
    TimelineSelectionEventCallback,
    TimelineSelectionRuntime,
)


def build_timeline_selection_runtime(
    *,
    production_id: str,
    duration: float,
    tracks: list[Any] | None = None,
    fps: float = 30.0,
    event_callback: (
        TimelineSelectionEventCallback | None
    ) = None,
) -> TimelineSelectionRuntime:
    catalog = build_selection_catalog(
        production_id=production_id,
        duration=duration,
        tracks=tracks or [],
        fps=fps,
    )

    return TimelineSelectionRuntime(
        catalog=catalog,
        event_callback=event_callback,
    )


def build_timeline_selection_from_workspace(
    workspace: Any,
    *,
    event_callback: (
        TimelineSelectionEventCallback | None
    ) = None,
) -> TimelineSelectionRuntime:
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

    production_id = _read(
        production,
        "production_id",
        "",
    )

    if not production_id:
        raise ValueError(
            "Workspace does not contain "
            "production_id."
        )

    canvas = _read(
        timeline,
        "canvas",
        {},
    )

    return build_timeline_selection_runtime(
        production_id=str(
            production_id
        ),
        duration=float(
            _read(
                timeline,
                "duration",
                0.0,
            )
            or 0.0
        ),
        tracks=list(
            _read(
                timeline,
                "tracks",
                [],
            )
            or []
        ),
        fps=float(
            _read(
                canvas,
                "fps",
                30.0,
            )
            or 30.0
        ),
        event_callback=event_callback,
    )


def build_selection_catalog(
    *,
    production_id: str,
    duration: float,
    tracks: list[Any],
    fps: float = 30.0,
) -> TimelineSelectionCatalog:
    selectable_tracks: list[
        TimelineSelectableTrack
    ] = []

    selectable_clips: list[
        TimelineSelectableClip
    ] = []

    for index, track in enumerate(
        tracks
    ):
        track_id = str(
            _read(
                track,
                "track_id",
                _read(
                    track,
                    "id",
                    f"track_{index}",
                ),
            )
        )

        raw_clips = list(
            _read(
                track,
                "clips",
                [],
            )
            or []
        )

        clip_ids: list[str] = []

        for clip_index, clip in enumerate(
            raw_clips
        ):
            clip_id = str(
                _read(
                    clip,
                    "clip_id",
                    _read(
                        clip,
                        "id",
                        (
                            f"{track_id}_"
                            f"clip_{clip_index}"
                        ),
                    ),
                )
            )

            clip_ids.append(clip_id)

            selectable_clips.append(
                TimelineSelectableClip(
                    clip_id=clip_id,
                    track_id=track_id,
                    start_time=float(
                        _read(
                            clip,
                            "start_time",
                            _read(
                                clip,
                                "timeline_start",
                                0.0,
                            ),
                        )
                        or 0.0
                    ),
                    end_time=float(
                        _read(
                            clip,
                            "end_time",
                            _read(
                                clip,
                                "timeline_end",
                                0.0,
                            ),
                        )
                        or 0.0
                    ),
                    clip_type=_enum_value(
                        _read(
                            clip,
                            "clip_type",
                            _read(
                                clip,
                                "type",
                            ),
                        )
                    ),
                    metadata={
                        "source": (
                            "timeline_workspace"
                        ),
                    },
                )
            )

        selectable_tracks.append(
            TimelineSelectableTrack(
                track_id=track_id,
                track_type=_enum_value(
                    _read(
                        track,
                        "track_type",
                        _read(
                            track,
                            "type",
                        ),
                    )
                ),
                name=_read(
                    track,
                    "name",
                ),
                position=int(
                    _read(
                        track,
                        "position",
                        index,
                    )
                    or 0
                ),
                clip_ids=tuple(clip_ids),
                metadata={
                    "source": (
                        "timeline_workspace"
                    ),
                },
            )
        )

    return TimelineSelectionCatalog(
        production_id=production_id,
        duration=duration,
        tracks=tuple(
            selectable_tracks
        ),
        clips=tuple(
            selectable_clips
        ),
        fps=fps,
        metadata={
            "builder": (
                "build_selection_catalog"
            ),
        },
    )


def _read(
    source: Any,
    key: str,
    default: Any = None,
) -> Any:
    if source is None:
        return default

    if isinstance(source, dict):
        return source.get(key, default)

    return getattr(
        source,
        key,
        default,
    )


def _enum_value(
    value: Any,
) -> str | None:
    if value is None:
        return None

    if hasattr(value, "value"):
        return str(value.value)

    return str(value)