from __future__ import annotations


DEFAULT_MIX_ORDER = [
    "voice",
    "music",
    "sfx",
    "ducking",
    "master",
]


def default_master_chain() -> list[dict]:
    return [
        {
            "operation": "normalize_audio",
            "parameters": {
                "target_lufs": -14,
                "true_peak": -1.0,
            },
        },
        {
            "operation": "limit_audio",
            "parameters": {
                "ceiling_db": -1.0,
            },
        },
    ]