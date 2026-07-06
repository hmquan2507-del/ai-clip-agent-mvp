from __future__ import annotations

from typing import Any


def priority_from_score(score: float) -> str:
    if score >= 0.75:
        return "high"

    if score >= 0.45:
        return "medium"

    return "low"


def get_style_value(
    style_result: dict[str, Any],
    key: str,
    default: str,
) -> str:
    editing_style = style_result.get("editing_style", {})

    if not isinstance(editing_style, dict):
        return default

    value = editing_style.get(key)

    if not isinstance(value, str) or not value:
        return default

    return value


def should_add_zoom(
    style_result: dict[str, Any],
    priority: str,
) -> bool:
    zoom_frequency = get_style_value(
        style_result=style_result,
        key="zoom_frequency",
        default="medium",
    )

    if zoom_frequency == "high":
        return priority in {"high", "medium"}

    if zoom_frequency in {"medium", "low_medium"}:
        return priority == "high"

    return False


def should_add_sfx(
    style_result: dict[str, Any],
    priority: str,
) -> bool:
    sfx_style = get_style_value(
        style_result=style_result,
        key="sfx_style",
        default="minimal_pop",
    )

    if sfx_style in {"punchy", "minimal_pop", "light_marker"}:
        return priority in {"high", "medium"}

    return priority == "high"


def should_add_broll(
    style_result: dict[str, Any],
    priority: str,
) -> bool:
    broll_strategy = get_style_value(
        style_result=style_result,
        key="broll_strategy",
        default="support_key_points",
    )

    if broll_strategy in {
        "frequent_pattern_interrupts",
        "explain_concepts",
        "topic_based",
        "support_key_points",
    }:
        return priority in {"high", "medium"}

    return False