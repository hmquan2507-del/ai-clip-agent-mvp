from __future__ import annotations

from typing import Any


def infer_style_profile(
    hook_result: dict[str, Any],
    story_result: dict[str, Any],
    emotion_result: dict[str, Any],
) -> tuple[str, list[str]]:
    reasons: list[str] = []

    dominant_emotion = emotion_result.get("dominant_emotion", "neutral")
    average_intensity = float(emotion_result.get("average_intensity", 0.0) or 0.0)

    hooks = hook_result.get("hooks", [])
    arcs = story_result.get("arcs", [])

    if hooks and average_intensity >= 0.35:
        reasons.append("strong_hook_and_high_emotion")
        return "viral_short", reasons

    if dominant_emotion in {"curiosity", "surprise", "urgency"}:
        reasons.append(f"dominant_emotion:{dominant_emotion}")
        return "viral_short", reasons

    if arcs:
        arc_type = arcs[0].get("arc_type") if isinstance(arcs[0], dict) else None

        if arc_type in {"problem_solution_payoff", "setup_problem_insight"}:
            reasons.append(f"story_arc:{arc_type}")
            return "education", reasons

    if dominant_emotion in {"trust"}:
        reasons.append("trust_based_content")
        return "podcast", reasons

    reasons.append("default_talking_head")
    return "talking_head", reasons


def adjust_style_by_emotion(
    plan: dict[str, str],
    emotion_result: dict[str, Any],
) -> tuple[dict[str, str], list[str]]:
    adjusted = dict(plan)
    reasons: list[str] = []

    dominant_emotion = emotion_result.get("dominant_emotion", "neutral")
    average_intensity = float(emotion_result.get("average_intensity", 0.0) or 0.0)

    if dominant_emotion in {"pain", "urgency"}:
        adjusted["cut_speed"] = "fast"
        adjusted["zoom_frequency"] = "high"
        adjusted["sfx_style"] = "punchy"
        reasons.append(f"emotion_adjustment:{dominant_emotion}")

    if dominant_emotion in {"trust"}:
        adjusted["cut_speed"] = "slow_medium"
        adjusted["camera_motion"] = "minimal"
        adjusted["music_style"] = "calm_focus"
        reasons.append("emotion_adjustment:trust")

    if average_intensity >= 0.45:
        adjusted["caption_density"] = "high"
        adjusted["highlight_strategy"] = "emotional_words_and_numbers"
        reasons.append("high_average_intensity")

    return adjusted, reasons