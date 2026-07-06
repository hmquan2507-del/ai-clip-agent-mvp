from __future__ import annotations

from typing import Any


def build_subtitle_style(
    node_parameters: dict[str, Any],
    priority: str,
) -> dict[str, Any]:
    style = {
        "font_weight": node_parameters.get("font_weight", "normal"),
        "highlight": bool(node_parameters.get("highlight", False)),
        "emphasis_level": node_parameters.get("emphasis_level", "light"),
    }

    if priority == "high":
        style["font_weight"] = node_parameters.get("font_weight", "bold")
        style["highlight"] = True
        style["emphasis_level"] = node_parameters.get("emphasis_level", "strong")

    if priority == "medium":
        style["font_weight"] = node_parameters.get("font_weight", "semibold")
        style["highlight"] = bool(node_parameters.get("highlight", True))
        style["emphasis_level"] = node_parameters.get("emphasis_level", "medium")

    return style


def subtitle_animation(
    node_parameters: dict[str, Any],
    priority: str,
) -> str:
    animation = str(node_parameters.get("animation") or "none")

    if animation != "none":
        return animation

    if priority == "high":
        return "pop"

    if priority == "medium":
        return "fade"

    return "none"