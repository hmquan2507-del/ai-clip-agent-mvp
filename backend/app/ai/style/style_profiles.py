from __future__ import annotations


DEFAULT_STYLE_PROFILE = "talking_head"


STYLE_PROFILES: dict[str, dict[str, str]] = {
    "talking_head": {
        "subtitle_style": "bold_dynamic",
        "caption_density": "medium",
        "camera_motion": "subtle_zoom",
        "broll_strategy": "support_key_points",
        "music_style": "light_background",
        "sfx_style": "minimal_pop",
        "transition_style": "clean_cut",
        "cut_speed": "medium",
        "highlight_strategy": "keywords_only",
        "zoom_frequency": "medium",
    },
    "podcast": {
        "subtitle_style": "clean_readable",
        "caption_density": "medium",
        "camera_motion": "minimal",
        "broll_strategy": "topic_based",
        "music_style": "low_energy_background",
        "sfx_style": "very_minimal",
        "transition_style": "simple_cut",
        "cut_speed": "slow_medium",
        "highlight_strategy": "important_sentences",
        "zoom_frequency": "low",
    },
    "education": {
        "subtitle_style": "clear_structured",
        "caption_density": "high",
        "camera_motion": "minimal",
        "broll_strategy": "explain_concepts",
        "music_style": "calm_focus",
        "sfx_style": "light_marker",
        "transition_style": "section_cut",
        "cut_speed": "medium",
        "highlight_strategy": "definitions_and_numbers",
        "zoom_frequency": "low_medium",
    },
    "viral_short": {
        "subtitle_style": "bold_high_contrast",
        "caption_density": "high",
        "camera_motion": "active_zoom",
        "broll_strategy": "frequent_pattern_interrupts",
        "music_style": "high_energy",
        "sfx_style": "punchy",
        "transition_style": "fast_cut",
        "cut_speed": "fast",
        "highlight_strategy": "emotional_words_and_numbers",
        "zoom_frequency": "high",
    },
}