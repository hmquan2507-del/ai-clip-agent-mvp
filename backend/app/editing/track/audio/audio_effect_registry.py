from __future__ import annotations


VOICE_OPERATIONS = {
    "enhance_voice",
    "cleanup_voice",
    "noise_reduction",
}

MUSIC_OPERATIONS = {
    "add_background_music",
    "fade_music_in",
    "fade_music_out",
    "adjust_music",
}

SFX_OPERATIONS = {
    "insert_sound_effect",
    "add_pop_or_impact_sfx",
    "add_excitement_sfx",
    "add_surprise_sfx",
    "add_urgency_sfx",
}

DUCKING_OPERATIONS = {
    "duck_music",
    "sidechain_music",
    "voice_priority_ducking",
}

MASTER_OPERATIONS = {
    "normalize_audio",
    "limit_audio",
    "compress_audio",
}


def classify_audio_operation(operation: str, track: str) -> str:
    if track == "audio":
        return "voice"

    if track == "music":
        return "music"

    if track == "sfx":
        return "sfx"

    if operation in VOICE_OPERATIONS or "voice" in operation or "noise" in operation:
        return "voice"

    if operation in MUSIC_OPERATIONS or "music" in operation:
        return "music"

    if operation in SFX_OPERATIONS or "sfx" in operation or "sound" in operation:
        return "sfx"

    if operation in DUCKING_OPERATIONS or "duck" in operation:
        return "ducking"

    if operation in MASTER_OPERATIONS or "normalize" in operation or "limit" in operation:
        return "master"

    return "voice"