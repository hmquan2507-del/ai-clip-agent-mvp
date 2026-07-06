from __future__ import annotations


CAMERA_OPERATIONS = {
    "apply_zoom",
    "apply_hook_zoom",
    "apply_problem_zoom",
    "apply_curiosity_zoom",
    "apply_surprise_zoom",
}

BROLL_OPERATIONS = {
    "insert_broll",
    "insert_insight_supporting_broll",
    "insert_payoff_supporting_broll",
}

OVERLAY_OPERATIONS = {
    "apply_overlay",
    "add_callout",
    "add_sticker",
    "add_visual_highlight",
}

TRANSITION_OPERATIONS = {
    "apply_transition",
    "fast_cut",
    "clean_cut",
}


def classify_video_operation(operation: str, track: str) -> str:
    if track == "camera_motion":
        return "camera_motion"

    if track == "broll":
        return "broll"

    if operation in CAMERA_OPERATIONS or "zoom" in operation:
        return "camera_motion"

    if operation in BROLL_OPERATIONS or "broll" in operation:
        return "broll"

    if operation in OVERLAY_OPERATIONS or "overlay" in operation:
        return "overlay"

    if operation in TRANSITION_OPERATIONS or "transition" in operation:
        return "transition"

    return "base"