from __future__ import annotations

from pathlib import Path
from typing import Any

from app.product.workspace.interfaces import (
    TimelineWorkspaceLoader,
)
from app.product.workspace.repository.utils import (
    call_first_supported,
    find_first_json,
    normalize_production_id,
)


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

        return find_first_json(
            self._timeline_candidates(
                normalized_id
            )
        )

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

        if self.include_demo_fallbacks:
            candidates.extend(
                [
                    Path(
                        "storage/demo_outputs/"
                        "final_timeline.json"
                    ),
                    Path(
                        "storage/demo_outputs/"
                        "execution_timeline.json"
                    ),
                ]
            )

        return candidates