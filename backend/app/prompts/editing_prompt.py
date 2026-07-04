from __future__ import annotations


def build_editing_prompt(
    transcript: str,
    target_duration_seconds: int | None = None,
) -> str:
    target = (
        f"{target_duration_seconds} seconds"
        if target_duration_seconds
        else "best possible duration"
    )

    return f"""
You are an expert short-form video editor.

Your task is to analyze the transcript and create an editing plan.

Target duration:
{target}

Transcript:

{transcript}

Return JSON only.

The JSON must contain:

- summary
- segments

Each segment contains:

- start_time
- end_time
- action
- reason
- priority

Allowed actions:

KEEP
CUT
HOOK
HIGHLIGHT
BROLL
SOUND_EFFECT
SUBTITLE_EMPHASIS
"""