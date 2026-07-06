from __future__ import annotations


def zoom_parameters(priority: str) -> dict:
    if priority == "high":
        return {
            "start_scale": 1.0,
            "end_scale": 1.18,
            "easing": "ease_out",
        }

    if priority == "medium":
        return {
            "start_scale": 1.0,
            "end_scale": 1.12,
            "easing": "ease_out",
        }

    return {
        "start_scale": 1.0,
        "end_scale": 1.08,
        "easing": "linear",
    }


def subtitle_emphasis_parameters(priority: str) -> dict:
    if priority == "high":
        return {
            "font_weight": "bold",
            "highlight": True,
            "animation": "pop",
            "emphasis_level": "strong",
        }

    if priority == "medium":
        return {
            "font_weight": "semibold",
            "highlight": True,
            "animation": "fade",
            "emphasis_level": "medium",
        }

    return {
        "font_weight": "normal",
        "highlight": False,
        "animation": "none",
        "emphasis_level": "light",
    }


def sfx_parameters(action: str, priority: str) -> dict:
    return {
        "sfx_type": "impact" if priority == "high" else "pop",
        "action": action,
        "volume": 0.8 if priority == "high" else 0.55,
        "duck_music": priority == "high",
    }


def broll_parameters(action: str, priority: str) -> dict:
    return {
        "broll_type": "supporting_visual",
        "action": action,
        "density": "high" if priority == "high" else "medium",
        "match_topic": True,
    }


def pace_parameters(action: str, priority: str) -> dict:
    return {
        "action": action,
        "cut_speed": "fast" if priority in {"high", "medium"} else "medium",
        "remove_silence": priority == "high",
        "tighten_gaps": True,
    }


def global_style_parameters(editing_style: dict) -> dict:
    return {
        "editing_style": editing_style,
        "apply_to": "full_timeline",
    }