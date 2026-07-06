from __future__ import annotations

from app.ai.style.models import EditingStylePlan
from app.ai.style.style_profiles import DEFAULT_STYLE_PROFILE, STYLE_PROFILES


def build_style_plan(
    profile_key: str,
    reasons: list[str],
) -> EditingStylePlan:
    profile = STYLE_PROFILES.get(profile_key) or STYLE_PROFILES[DEFAULT_STYLE_PROFILE]

    return EditingStylePlan(
        subtitle_style=profile["subtitle_style"],
        caption_density=profile["caption_density"],
        camera_motion=profile["camera_motion"],
        broll_strategy=profile["broll_strategy"],
        music_style=profile["music_style"],
        sfx_style=profile["sfx_style"],
        transition_style=profile["transition_style"],
        cut_speed=profile["cut_speed"],
        highlight_strategy=profile["highlight_strategy"],
        zoom_frequency=profile["zoom_frequency"],
        reasons=reasons,
    )


def build_style_plan_from_dict(
    profile: dict[str, str],
    reasons: list[str],
) -> EditingStylePlan:
    return EditingStylePlan(
        subtitle_style=profile["subtitle_style"],
        caption_density=profile["caption_density"],
        camera_motion=profile["camera_motion"],
        broll_strategy=profile["broll_strategy"],
        music_style=profile["music_style"],
        sfx_style=profile["sfx_style"],
        transition_style=profile["transition_style"],
        cut_speed=profile["cut_speed"],
        highlight_strategy=profile["highlight_strategy"],
        zoom_frequency=profile["zoom_frequency"],
        reasons=reasons,
    )