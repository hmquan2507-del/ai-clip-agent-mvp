from __future__ import annotations

import json
from typing import Any

from app.product.workspace.interfaces import (
    AISummaryWorkspaceLoader,
)
from app.product.workspace.repository.utils import (
    call_first_supported,
    normalize_production_id,
    plain_value,
    value_of,
)


class RepositoryAISummaryWorkspaceAdapter(
    AISummaryWorkspaceLoader
):
    METHOD_NAMES = (
        "get_latest_by_production",
        "get_by_production_id",
        "find_by_production_id",
        "get_latest_by_production_id",
        "get_content_graph",
        "get_summary",
    )

    def __init__(
        self,
        ai_repository: Any | None = None,
    ):
        self.ai_repository = (
            ai_repository
        )

    def load_ai_summary(
        self,
        production_id: str,
    ) -> dict[str, Any]:
        normalized_id = (
            normalize_production_id(
                production_id
            )
        )

        source = call_first_supported(
            self.ai_repository,
            self.METHOD_NAMES,
            production_id=normalized_id,
            default=None,
        )

        if source is None:
            return {}

        if isinstance(
            source,
            dict,
        ):
            return self._from_mapping(
                source
            )

        return self._from_content_graph(
            source
        )

    def _from_content_graph(
        self,
        source: Any,
    ) -> dict[str, Any]:
        segments: list[
            dict[str, Any]
        ] = []

        for segment in getattr(
            source,
            "segments",
            [],
        ) or []:
            segment_type = getattr(
                segment,
                "type",
                None,
            )

            if hasattr(
                segment_type,
                "value",
            ):
                segment_type = (
                    segment_type.value
                )

            emotion = getattr(
                segment,
                "emotion",
                None,
            )

            if hasattr(
                emotion,
                "value",
            ):
                emotion = emotion.value

            segments.append(
                {
                    "segment_id": str(
                        getattr(
                            segment,
                            "id",
                            "",
                        )
                    ),
                    "start_time": (
                        getattr(
                            segment,
                            "start_time",
                            None,
                        )
                    ),
                    "end_time": (
                        getattr(
                            segment,
                            "end_time",
                            None,
                        )
                    ),
                    "text": getattr(
                        segment,
                        "text",
                        None,
                    ),
                    "segment_type": (
                        segment_type
                    ),
                    "emotion": emotion,
                    "topic": getattr(
                        segment,
                        "topic",
                        None,
                    ),
                    "importance_score": (
                        getattr(
                            segment,
                            "importance_score",
                            None,
                        )
                    ),
                    "viral_potential_score": (
                        getattr(
                            segment,
                            "viral_potential_score",
                            None,
                        )
                    ),
                    "speaker_id": (
                        getattr(
                            segment,
                            "speaker_id",
                            None,
                        )
                    ),
                    "order_index": (
                        getattr(
                            segment,
                            "order_index",
                            None,
                        )
                    ),
                }
            )

        status = getattr(
            source,
            "status",
            None,
        )

        if hasattr(
            status,
            "value",
        ):
            status = status.value

        return {
            "summary": getattr(
                source,
                "summary",
                None,
            ),
            "topics": (
                self._parse_json_value(
                    getattr(
                        source,
                        "topic_json",
                        None,
                    )
                )
            ),
            "speakers": (
                self._parse_json_value(
                    getattr(
                        source,
                        "speaker_json",
                        None,
                    )
                )
            ),
            "segments": segments,
            "metadata": {
                "source": (
                    "ContentGraphRepository"
                ),
                "content_graph_id": str(
                    getattr(
                        source,
                        "id",
                        "",
                    )
                ),
                "status": status,
                "language": getattr(
                    source,
                    "language",
                    None,
                ),
                "runtime_metadata": (
                    self._parse_json_value(
                        getattr(
                            source,
                            "metadata_json",
                            None,
                        )
                    )
                ),
            },
        }

    def _from_mapping(
        self,
        source: dict[str, Any],
    ) -> dict[str, Any]:
        allowed_keys = (
            "summary",
            "hook",
            "hook_summary",
            "story_type",
            "emotion",
            "dominant_emotion",
            "editing_style",
            "decision_summary",
            "keywords",
            "topics",
            "speakers",
            "segments",
        )

        result = {
            key: source[key]
            for key in allowed_keys
            if key in source
        }

        if (
            "hook" not in result
            and "hook_summary" in result
        ):
            result["hook"] = (
                result["hook_summary"]
            )

        if (
            "emotion" not in result
            and "dominant_emotion"
            in result
        ):
            result["emotion"] = (
                result[
                    "dominant_emotion"
                ]
            )

        result["story_type"] = (
            plain_value(
                result.get(
                    "story_type"
                )
            )
        )

        result["emotion"] = (
            plain_value(
                result.get(
                    "emotion"
                )
            )
        )

        result["editing_style"] = (
            plain_value(
                result.get(
                    "editing_style"
                )
            )
        )

        result["metadata"] = {
            "source": (
                "repository_mapping"
            ),
        }

        return result

    def _parse_json_value(
        self,
        value: Any,
    ) -> Any:
        if value is None:
            return None

        if not isinstance(
            value,
            str,
        ):
            return value

        stripped = value.strip()

        if not stripped:
            return None

        try:
            return json.loads(
                stripped
            )
        except json.JSONDecodeError:
            return value