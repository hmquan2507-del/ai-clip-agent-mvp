from __future__ import annotations

from typing import Any


def instruction_type_from_layer(
    layer_type: str,
    operation: str,
) -> str:
    if layer_type == "subtitle":
        return "subtitle"

    if layer_type in {"base_video", "video_effect"}:
        if "zoom" in operation:
            return "camera_motion"

        return "video_effect"

    if layer_type == "visual_overlay":
        return "visual_overlay"

    if layer_type == "transition":
        return "transition"

    if layer_type in {"voice", "music", "sound_effect"}:
        return "audio_mix"

    if layer_type == "mix_control":
        return "audio_ducking"

    if layer_type == "master_bus":
        return "audio_mastering"

    return "generic"


def render_operation_from_instruction(
    instruction_type: str,
    raw_operation: str,
) -> str:
    if instruction_type == "subtitle":
        return "render_subtitle"

    if instruction_type == "camera_motion":
        return "apply_camera_motion"

    if instruction_type == "video_effect":
        return "apply_video_effect"

    if instruction_type == "visual_overlay":
        return "render_visual_overlay"

    if instruction_type == "transition":
        return "apply_transition"

    if instruction_type == "audio_mix":
        return "mix_audio_layer"

    if instruction_type == "audio_ducking":
        return "apply_audio_ducking"

    if instruction_type == "audio_mastering":
        return "apply_audio_mastering"

    return raw_operation or "render_generic_instruction"


def default_outputs(
    layer_key: str,
    instruction_type: str,
) -> dict[str, Any]:
    return {
        "target": f"{layer_key}_{instruction_type}_output",
    }