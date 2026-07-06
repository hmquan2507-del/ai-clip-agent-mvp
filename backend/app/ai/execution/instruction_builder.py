from __future__ import annotations

from typing import Any

from app.ai.execution.execution_rules import (
    broll_parameters,
    global_style_parameters,
    pace_parameters,
    sfx_parameters,
    subtitle_emphasis_parameters,
    zoom_parameters,
)
from app.ai.execution.models import TimelineInstruction


class InstructionBuilder:
    def build(self, decision: dict[str, Any]) -> list[TimelineInstruction]:
        decision_type = decision.get("decision_type")
        priority = decision.get("priority", "medium")
        action = decision.get("action", "")
        start_time = self._safe_float(decision.get("start_time", 0.0))
        end_time = self._safe_float(decision.get("end_time", start_time))
        reason = decision.get("reason", "")
        source_segment_id = decision.get("source_segment_id")

        if decision_type == "global_style":
            editing_style = decision.get("metadata", {}).get("editing_style", {})
            return [
                TimelineInstruction(
                    instruction_type="global_style",
                    start_time=0.0,
                    end_time=0.0,
                    track="global",
                    operation="apply_global_style",
                    parameters=global_style_parameters(editing_style),
                    priority=priority,
                    reason=reason,
                    source_decision_type=decision_type,
                    source_segment_id=source_segment_id,
                )
            ]

        if decision_type == "subtitle_emphasis":
            return [
                TimelineInstruction(
                    instruction_type="subtitle",
                    start_time=start_time,
                    end_time=end_time,
                    track="subtitle",
                    operation="apply_subtitle_emphasis",
                    parameters=subtitle_emphasis_parameters(priority),
                    priority=priority,
                    reason=reason,
                    source_decision_type=decision_type,
                    source_segment_id=source_segment_id,
                )
            ]

        if decision_type == "zoom_in":
            return [
                TimelineInstruction(
                    instruction_type="camera_motion",
                    start_time=start_time,
                    end_time=end_time,
                    track="video",
                    operation="apply_zoom",
                    parameters=zoom_parameters(priority),
                    priority=priority,
                    reason=reason,
                    source_decision_type=decision_type,
                    source_segment_id=source_segment_id,
                )
            ]

        if decision_type == "sound_effect":
            return [
                TimelineInstruction(
                    instruction_type="audio_sfx",
                    start_time=start_time,
                    end_time=end_time,
                    track="audio",
                    operation="insert_sound_effect",
                    parameters=sfx_parameters(action, priority),
                    priority=priority,
                    reason=reason,
                    source_decision_type=decision_type,
                    source_segment_id=source_segment_id,
                )
            ]

        if decision_type == "broll":
            return [
                TimelineInstruction(
                    instruction_type="broll",
                    start_time=start_time,
                    end_time=end_time,
                    track="visual_overlay",
                    operation="insert_broll",
                    parameters=broll_parameters(action, priority),
                    priority=priority,
                    reason=reason,
                    source_decision_type=decision_type,
                    source_segment_id=source_segment_id,
                )
            ]

        if decision_type == "pace_change":
            return [
                TimelineInstruction(
                    instruction_type="timeline_pacing",
                    start_time=start_time,
                    end_time=end_time,
                    track="timeline",
                    operation="adjust_pacing",
                    parameters=pace_parameters(action, priority),
                    priority=priority,
                    reason=reason,
                    source_decision_type=decision_type,
                    source_segment_id=source_segment_id,
                )
            ]

        return []

    def _safe_float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0