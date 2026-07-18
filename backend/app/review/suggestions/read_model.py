from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
from typing import Any, Callable, Iterable, Mapping

from app.review.suggestions.enums import (
    AISuggestionKind,
    AISuggestionStatus,
    AISuggestionTargetType,
)
from app.review.suggestions.models import (
    AISuggestion,
    AISuggestionCommandProposal,
    AISuggestionReadModel,
    AISuggestionTarget,
    utc_now_iso,
)


RawSuggestion = str | Mapping[str, Any]


class AISuggestionReadModelBuilder:
    def __init__(
        self,
        *,
        now: Callable[[], str] = utc_now_iso,
    ):
        self._now = now

    def build(
        self,
        *,
        production_id: str,
        timeline_revision: int,
        raw_suggestions: Iterable[
            RawSuggestion
        ] = (),
        ai_metadata: (
            Mapping[str, Any] | None
        ) = None,
        selected_suggestion_id: (
            str | None
        ) = None,
    ) -> AISuggestionReadModel:
        production_id = _identifier(
            production_id,
            "production_id",
        )
        timeline_revision = _positive_integer(
            timeline_revision,
            "timeline_revision",
        )
        generated_at = self._now()

        suggestions = tuple(
            self._normalize(
                raw,
                index=index,
                production_id=production_id,
                active_timeline_revision=(
                    timeline_revision
                ),
                generated_at=generated_at,
            )
            for index, raw in enumerate(
                deepcopy(list(raw_suggestions))
            )
        )

        return AISuggestionReadModel(
            production_id=production_id,
            timeline_revision=timeline_revision,
            suggestions=suggestions,
            selected_suggestion_id=(
                selected_suggestion_id
            ),
            generated_at=generated_at,
            metadata={
                "source": "workspace.ai",
                "source_count": len(suggestions),
                "ai_metadata": deepcopy(
                    dict(ai_metadata or {})
                ),
            },
        )

    def _normalize(
        self,
        raw: RawSuggestion,
        *,
        index: int,
        production_id: str,
        active_timeline_revision: int,
        generated_at: str,
    ) -> AISuggestion:
        if isinstance(raw, str):
            data: dict[str, Any] = {
                "description": raw,
            }
        elif isinstance(raw, Mapping):
            data = deepcopy(dict(raw))
        else:
            raise TypeError(
                "AI suggestion at index "
                f"{index} must be a string or mapping."
            )

        description = _first_text(
            data,
            (
                "description",
                "message",
                "text",
                "content",
                "suggestion",
            ),
        ) or "Đề xuất chỉnh sửa từ AI"

        title = _first_text(
            data,
            ("title", "label", "name"),
        ) or _title_from_description(
            description
        )

        suggestion_revision = (
            _optional_positive_integer(
                data.get("timeline_revision")
            )
            or active_timeline_revision
        )
        status = _status(
            data.get("status")
        )

        if (
            status
            == AISuggestionStatus.PROPOSED
            and suggestion_revision
            != active_timeline_revision
        ):
            status = AISuggestionStatus.STALE

        target = _target(
            data.get("target"),
            production_id=production_id,
            fallback=data,
        )
        command = _command(
            data.get("command")
            or data.get("proposed_command")
            or data.get("action")
        )
        kind = _kind(
            data.get("kind")
            or data.get("type")
            or data.get("category")
        )
        score = _score(
            data.get("score")
            if data.get("score") is not None
            else data.get("confidence")
        )
        suggestion_id = _first_text(
            data,
            ("suggestion_id", "id"),
        ) or _stable_suggestion_id(
            production_id=production_id,
            timeline_revision=(
                suggestion_revision
            ),
            index=index,
            data=data,
        )

        known_fields = {
            "suggestion_id",
            "id",
            "kind",
            "type",
            "category",
            "status",
            "title",
            "label",
            "name",
            "description",
            "message",
            "text",
            "content",
            "suggestion",
            "timeline_revision",
            "target",
            "track_id",
            "clip_id",
            "start_time",
            "end_time",
            "command",
            "proposed_command",
            "action",
            "score",
            "confidence",
            "created_at",
            "metadata",
        }
        passthrough = {
            key: deepcopy(value)
            for key, value in data.items()
            if key not in known_fields
        }
        metadata = deepcopy(
            data.get("metadata")
            if isinstance(
                data.get("metadata"),
                Mapping,
            )
            else {}
        )
        metadata.update(passthrough)
        metadata["source_index"] = index

        suggestion = AISuggestion(
            suggestion_id=suggestion_id,
            production_id=production_id,
            kind=kind,
            status=status,
            title=title,
            description=description,
            timeline_revision=(
                suggestion_revision
            ),
            target=target,
            command=command,
            score=score,
            created_at=(
                _first_text(
                    data,
                    ("created_at",),
                )
                or generated_at
            ),
            metadata=metadata,
        )

        if (
            suggestion.timeline_revision
            != active_timeline_revision
            and not suggestion.stale
        ):
            return replace(
                suggestion,
                status=AISuggestionStatus.STALE,
            )

        return suggestion


def _target(
    raw: Any,
    *,
    production_id: str,
    fallback: Mapping[str, Any],
) -> AISuggestionTarget:
    data = (
        dict(raw)
        if isinstance(raw, Mapping)
        else {}
    )

    for key in (
        "track_id",
        "clip_id",
        "start_time",
        "end_time",
    ):
        if key not in data and key in fallback:
            data[key] = fallback[key]

    target_type = _target_type(
        data.get("target_type")
        or data.get("type"),
        data,
    )

    return AISuggestionTarget(
        production_id=production_id,
        target_type=target_type,
        track_id=_optional_text(
            data.get("track_id")
        ),
        clip_id=_optional_text(
            data.get("clip_id")
        ),
        start_time=_optional_number(
            data.get("start_time")
        ),
        end_time=_optional_number(
            data.get("end_time")
        ),
        metadata=(
            deepcopy(data.get("metadata"))
            if isinstance(
                data.get("metadata"),
                Mapping,
            )
            else {}
        ),
    )


def _command(
    raw: Any,
) -> AISuggestionCommandProposal | None:
    if raw is None:
        return None

    if isinstance(raw, str):
        operation = raw
        arguments: dict[str, Any] = {}
        metadata: dict[str, Any] = {}
    elif isinstance(raw, Mapping):
        data = dict(raw)
        operation = (
            data.get("operation")
            or data.get("command")
            or data.get("type")
        )
        if not operation:
            return None
        raw_arguments = (
            data.get("arguments")
            or data.get("payload")
            or data.get("params")
            or {}
        )
        if not isinstance(
            raw_arguments,
            Mapping,
        ):
            raise TypeError(
                "Suggestion command arguments must "
                "be a mapping."
            )
        arguments = deepcopy(
            dict(raw_arguments)
        )
        metadata = (
            deepcopy(dict(data["metadata"]))
            if isinstance(
                data.get("metadata"),
                Mapping,
            )
            else {}
        )
    else:
        raise TypeError(
            "Suggestion command must be a string "
            "or mapping."
        )

    return AISuggestionCommandProposal(
        operation=str(operation).strip(),
        arguments=arguments,
        metadata=metadata,
    )


def _kind(raw: Any) -> AISuggestionKind:
    normalized = str(
        raw or "generic"
    ).strip().lower().replace("-", "_")
    aliases = {
        "b_roll": AISuggestionKind.BROLL,
        "sfx": AISuggestionKind.SOUND_EFFECT,
        "soundeffect": (
            AISuggestionKind.SOUND_EFFECT
        ),
        "captions": AISuggestionKind.SUBTITLE,
    }
    if normalized in aliases:
        return aliases[normalized]
    try:
        return AISuggestionKind(normalized)
    except ValueError:
        return AISuggestionKind.GENERIC


def _status(raw: Any) -> AISuggestionStatus:
    normalized = str(
        raw or "proposed"
    ).strip().lower()
    aliases = {
        "new": AISuggestionStatus.PROPOSED,
        "active": AISuggestionStatus.PROPOSED,
        "ignored": AISuggestionStatus.DISMISSED,
        "rejected": AISuggestionStatus.DISMISSED,
    }
    if normalized in aliases:
        return aliases[normalized]
    try:
        return AISuggestionStatus(normalized)
    except ValueError:
        return AISuggestionStatus.PROPOSED


def _target_type(
    raw: Any,
    data: Mapping[str, Any],
) -> AISuggestionTargetType:
    if raw:
        try:
            return AISuggestionTargetType(
                str(raw).strip().lower()
            )
        except ValueError:
            pass
    if data.get("clip_id"):
        return AISuggestionTargetType.CLIP
    if data.get("track_id"):
        return AISuggestionTargetType.TRACK
    if (
        data.get("start_time") is not None
        or data.get("end_time") is not None
    ):
        return AISuggestionTargetType.RANGE
    return AISuggestionTargetType.TIMELINE


def _score(raw: Any) -> float | None:
    if raw is None:
        return None
    if isinstance(raw, bool):
        raise TypeError("score must be numeric.")
    value = float(raw)
    if 0 <= value <= 1:
        value *= 100
    if not 0 <= value <= 100:
        raise ValueError(
            "score must be between 0 and 100."
        )
    return round(value, 4)


def _stable_suggestion_id(
    *,
    production_id: str,
    timeline_revision: int,
    index: int,
    data: Mapping[str, Any],
) -> str:
    canonical = json.dumps(
        data,
        sort_keys=True,
        ensure_ascii=False,
        default=str,
        separators=(",", ":"),
    )
    digest = sha256(
        (
            f"{production_id}:"
            f"{timeline_revision}:"
            f"{index}:{canonical}"
        ).encode("utf-8")
    ).hexdigest()[:20]
    return f"ai-suggestion-{digest}"


def _title_from_description(
    description: str,
) -> str:
    normalized = " ".join(
        description.split()
    )
    if len(normalized) <= 72:
        return normalized
    return normalized[:69].rstrip() + "..."


def _first_text(
    data: Mapping[str, Any],
    keys: tuple[str, ...],
) -> str | None:
    for key in keys:
        value = _optional_text(data.get(key))
        if value:
            return value
    return None


def _optional_text(raw: Any) -> str | None:
    if raw is None:
        return None
    normalized = str(raw).strip()
    return normalized or None


def _optional_number(raw: Any) -> float | None:
    if raw is None:
        return None
    if isinstance(raw, bool):
        raise TypeError(
            "Timeline target time must be numeric."
        )
    return float(raw)


def _positive_integer(
    raw: Any,
    name: str,
) -> int:
    if isinstance(raw, bool):
        raise TypeError(
            f"{name} must be an integer."
        )
    value = int(raw)
    if value < 1:
        raise ValueError(
            f"{name} must be at least 1."
        )
    return value


def _optional_positive_integer(
    raw: Any,
) -> int | None:
    if raw is None:
        return None
    return _positive_integer(
        raw,
        "timeline_revision",
    )


def _identifier(raw: Any, name: str) -> str:
    normalized = str(raw).strip()
    if not normalized:
        raise ValueError(
            f"{name} must not be empty."
        )
    return normalized
