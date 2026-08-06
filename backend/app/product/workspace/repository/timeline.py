from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from app.product.workspace.interfaces import (
    TimelineWorkspaceLoader,
)
from app.product.workspace.repository.utils import (
    call_first_supported,
    find_first_json,
    normalize_production_id,
)

# The persisted Timeline's track/clip vocabulary (app/db/enums.py) is
# coarser than the Review Workspace's EditableTimeline vocabulary
# (app/review/editing/enums.py) - naively passing the DB string through
# fails EditableTrackType/EditableClipType's own coercion (e.g. DB "video"
# has no EditableTrackType member, only "video_primary" does) and
# silently degrades every video track to "unknown". Map back explicitly
# rather than relying on the two vocabularies happening to line up.
_DB_TRACK_TYPE_TO_EDITABLE = {
    "video": "video_primary",
    "audio": "audio",
    "subtitle": "subtitle",
    "broll": "broll",
    "sound_effect": "sound_effect",
    "music": "music",
}

_DB_CLIP_TYPE_TO_EDITABLE = {
    "source": "video",
    "generated": "audio",
    "subtitle": "subtitle",
    "broll": "broll",
    "sound_effect": "sound_effect",
    "music": "music",
}


class RepositoryTimelineWorkspaceAdapter(
    TimelineWorkspaceLoader
):
    METHOD_NAMES = (
        "get_latest_by_production",
        "get_latest_by_production_id",
        "find_latest_by_production_id",
        "get_by_production_id",
        "find_by_production_id",
        "get_timeline",
        "get_latest",
    )

    def __init__(
        self,
        timeline_repository: Any | None = None,
        *,
        storage_roots: list[str | Path] | None = None,
        include_demo_fallbacks: bool = True,
        default_source_lookup: (
            Callable[[str], dict[str, Any] | None] | None
        ) = None,
    ):
        self.timeline_repository = timeline_repository

        self.storage_roots = [
            Path(item)
            for item in (
                storage_roots
                or [
                    "storage/productions",
                    "storage/production_render",
                    "storage/render_end_to_end_demo",
                    "storage/render_execution_integration",
                ]
            )
        ]

        self.include_demo_fallbacks = (
            include_demo_fallbacks
        )

        # Called with production_id when no real, persisted timeline
        # exists yet (a brand new upload). Should return
        # {"asset_id", "local_path", "duration", "width", "height", "fps"}
        # for the production's real uploaded source video, or None.
        self.default_source_lookup = default_source_lookup

    def load_timeline(
        self,
        production_id: str,
    ) -> Any | None:
        normalized_id = normalize_production_id(
            production_id
        )

        repository_timeline = (
            call_first_supported(
                self.timeline_repository,
                self.METHOD_NAMES,
                production_id=normalized_id,
                default=None,
            )
        )

        if repository_timeline is not None:
            if isinstance(
                repository_timeline,
                dict,
            ):
                return repository_timeline

            return self._adapt_repository_timeline(
                repository_timeline
            )

        from_file = find_first_json(
            self._timeline_candidates(
                normalized_id
            )
        )

        if from_file is not None:
            return from_file

        return self._build_default_timeline_from_source(
            normalized_id
        )

    def _build_default_timeline_from_source(
        self,
        production_id: str,
    ) -> dict[str, Any] | None:
        if self.default_source_lookup is None:
            return None

        source = self.default_source_lookup(
            production_id
        )

        if not source or not source.get("local_path"):
            return None

        duration = float(source.get("duration") or 0.0)

        clip = {
            "clip_id": "source_clip",
            "clip_type": "video_primary",
            "start_time": 0.0,
            "end_time": duration,
            "source_start": 0.0,
            "source_end": duration,
            "asset_id": source.get("asset_id"),
            "local_path": source.get("local_path"),
            "metadata_json": None,
        }

        return {
            "production_id": production_id,
            "version": "1.0",
            "duration": duration,
            "canvas": {
                "width": source.get("width") or 1080,
                "height": source.get("height") or 1920,
                "fps": source.get("fps") or 30.0,
            },
            "tracks": [
                {
                    "track_id": "source_track",
                    "track_type": "video_primary",
                    "name": "Video chính",
                    "position": 0,
                    "clips": [clip],
                    "metadata_json": None,
                }
            ],
            "effects": [],
            "transitions": [],
            "metadata": {
                "source": "default_from_uploaded_asset",
            },
        }

    def _adapt_repository_timeline(
        self,
        timeline: Any,
    ) -> dict[str, Any]:
        tracks: list[dict[str, Any]] = []

        for track in getattr(
            timeline,
            "tracks",
            [],
        ) or []:
            clips: list[
                dict[str, Any]
            ] = []

            for clip in getattr(
                track,
                "clips",
                [],
            ) or []:
                clip_type = getattr(
                    clip,
                    "type",
                    None,
                )

                if hasattr(
                    clip_type,
                    "value",
                ):
                    clip_type = (
                        clip_type.value
                    )

                clip_type = _DB_CLIP_TYPE_TO_EDITABLE.get(
                    clip_type, clip_type
                )

                clips.append(
                    {
                        "clip_id": str(
                            getattr(
                                clip,
                                "id",
                                "",
                            )
                        ),
                        "clip_type": (
                            clip_type
                        ),
                        "start_time": float(
                            getattr(
                                clip,
                                "timeline_start",
                                0.0,
                            )
                            or 0.0
                        ),
                        "end_time": float(
                            getattr(
                                clip,
                                "timeline_end",
                                0.0,
                            )
                            or 0.0
                        ),
                        "source_start": (
                            getattr(
                                clip,
                                "source_start",
                                None,
                            )
                        ),
                        "source_end": (
                            getattr(
                                clip,
                                "source_end",
                                None,
                            )
                        ),
                        "asset_id": (
                            str(
                                getattr(
                                    clip,
                                    "asset_id",
                                )
                            )
                            if getattr(
                                clip,
                                "asset_id",
                                None,
                            )
                            is not None
                            else None
                        ),
                        "local_path": getattr(
                            clip,
                            "local_path",
                            None,
                        ),
                        "text": getattr(
                            clip,
                            "text",
                            None,
                        ),
                        "metadata_json": (
                            getattr(
                                clip,
                                "metadata_json",
                                None,
                            )
                        ),
                    }
                )

            track_type = getattr(
                track,
                "type",
                None,
            )

            if hasattr(
                track_type,
                "value",
            ):
                track_type = (
                    track_type.value
                )

            track_type = _DB_TRACK_TYPE_TO_EDITABLE.get(
                track_type, track_type
            )

            tracks.append(
                {
                    "track_id": str(
                        getattr(
                            track,
                            "id",
                            "",
                        )
                    ),
                    "track_type": (
                        track_type
                    ),
                    "name": getattr(
                        track,
                        "name",
                        None,
                    ),
                    "position": int(
                        getattr(
                            track,
                            "position",
                            0,
                        )
                        or 0
                    ),
                    "clips": clips,
                    "metadata_json": (
                        getattr(
                            track,
                            "metadata_json",
                            None,
                        )
                    ),
                }
            )

        status = getattr(
            timeline,
            "status",
            None,
        )

        if hasattr(
            status,
            "value",
        ):
            status = status.value

        production_id = getattr(
            timeline,
            "production_id",
            "",
        )

        return {
            "production_id": str(
                production_id
            ),
            "version": getattr(
                timeline,
                "version",
                None,
            ),
            "duration": float(
                getattr(
                    timeline,
                    "duration_seconds",
                    0.0,
                )
                or 0.0
            ),
            "canvas": {},
            "tracks": tracks,
            "effects": [],
            "transitions": [],
            "metadata": {
                "source": (
                    "TimelineRepository"
                ),
                "timeline_id": str(
                    getattr(
                        timeline,
                        "id",
                        "",
                    )
                ),
                "status": status,
            },
        }

    def _timeline_candidates(
        self,
        production_id: str,
    ) -> list[Path]:
        # Deliberately production_id-scoped only. This adapter previously
        # also fell back to global, unscoped files under
        # storage/demo_outputs/ whenever include_demo_fallbacks was true -
        # meaning every production with no real timeline yet (e.g. a
        # brand new upload) silently got served an unrelated demo
        # production's timeline as if it were real. Never fake success:
        # a production with no real timeline gets none, not someone
        # else's.
        candidates: list[
            Path
        ] = []

        for root in self.storage_roots:
            candidates.extend(
                [
                    root
                    / production_id
                    / "artifacts"
                    / "final_timeline.json",

                    root
                    / production_id
                    / "artifacts"
                    / "timeline.json",

                    root
                    / production_id
                    / "final_timeline.json",

                    root
                    / production_id
                    / "timeline.json",
                ]
            )

        return candidates