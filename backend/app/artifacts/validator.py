from __future__ import annotations

from typing import Any

from app.artifacts import keys


REQUIRED_RUNTIME_ARTIFACTS = [
    keys.EDITING_EXECUTION_PLANNER,
    keys.TIMELINE,
    keys.EXECUTION_GRAPH,
    keys.OPTIMIZED_EXECUTION_GRAPH,
    keys.TRACK_CONTEXT,
    keys.SUBTITLE_TRACK,
    keys.VIDEO_TRACK,
    keys.AUDIO_TRACK,
    keys.COMPOSITION,
    keys.RENDER_INSTRUCTIONS,
    keys.RENDER_PLAN,
    keys.RENDER_GRAPH,
    keys.RENDER_SCHEDULE,
    keys.RESOLVED_ASSETS,
    keys.FFMPEG_COMMAND_PLAN,
]


class RuntimeArtifactValidator:
    def validate(
        self,
        production_id: str,
        artifacts: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        missing: list[str] = []
        warnings: list[str] = []

        for artifact_key in REQUIRED_RUNTIME_ARTIFACTS:
            if artifact_key not in artifacts:
                missing.append(artifact_key)

        self._validate_editing_execution_planner(artifacts, warnings)
        self._validate_timeline(artifacts, warnings)
        self._validate_track_outputs(artifacts, warnings)
        self._validate_render_outputs(artifacts, warnings)

        return {
            "production_id": production_id,
            "is_valid": len(missing) == 0,
            "missing_artifacts": missing,
            "warnings": warnings,
            "artifact_count": len(artifacts),
            "required_count": len(REQUIRED_RUNTIME_ARTIFACTS),
        }

    def _validate_editing_execution_planner(
        self,
        artifacts: dict[str, dict[str, Any]],
        warnings: list[str],
    ) -> None:
        payload = artifacts.get(keys.EDITING_EXECUTION_PLANNER, {})
        instructions = payload.get("instructions", [])

        if not isinstance(instructions, list) or len(instructions) == 0:
            warnings.append("editing_execution_planner_has_no_instructions")

    def _validate_timeline(
        self,
        artifacts: dict[str, dict[str, Any]],
        warnings: list[str],
    ) -> None:
        payload = artifacts.get(keys.TIMELINE, {})
        metadata = payload.get("metadata", {})

        if isinstance(metadata, dict):
            if int(metadata.get("instruction_count", 0) or 0) == 0:
                warnings.append("timeline_instruction_count_is_zero")

            if int(metadata.get("event_count", 0) or 0) == 0:
                warnings.append("timeline_event_count_is_zero")

    def _validate_track_outputs(
        self,
        artifacts: dict[str, dict[str, Any]],
        warnings: list[str],
    ) -> None:
        subtitle = artifacts.get(keys.SUBTITLE_TRACK, {})
        subtitle_events = subtitle.get("events", [])
        if not isinstance(subtitle_events, list) or len(subtitle_events) == 0:
            warnings.append("subtitle_track_has_no_events")

        video = artifacts.get(keys.VIDEO_TRACK, {})
        video_layers = video.get("layers", [])
        if isinstance(video_layers, list):
            video_event_count = sum(
                len(layer.get("events", []))
                for layer in video_layers
                if isinstance(layer, dict) and isinstance(layer.get("events"), list)
            )
            if video_event_count == 0:
                warnings.append("video_track_has_no_events")

    def _validate_render_outputs(
        self,
        artifacts: dict[str, dict[str, Any]],
        warnings: list[str],
    ) -> None:
        render_plan = artifacts.get(keys.RENDER_PLAN, {})
        steps = render_plan.get("steps", [])
        if not isinstance(steps, list) or len(steps) == 0:
            warnings.append("render_plan_has_no_steps")

        command_plan = artifacts.get(keys.FFMPEG_COMMAND_PLAN, {})
        commands = command_plan.get("commands", [])
        if not isinstance(commands, list) or len(commands) == 0:
            warnings.append("ffmpeg_command_plan_has_no_commands")