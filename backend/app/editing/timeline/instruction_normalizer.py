from __future__ import annotations

from typing import Any

from app.editing.timeline.models import TimelineEvent


class TimelineInstructionNormalizer:
    def normalize(self, instruction: dict[str, Any]) -> TimelineEvent | None:
        instruction_type = instruction.get("instruction_type")
        start_time = self._safe_float(instruction.get("start_time", 0.0))
        end_time = self._safe_float(instruction.get("end_time", start_time))
        track = str(instruction.get("track") or "timeline")
        operation = str(instruction.get("operation") or "")

        if not instruction_type or not operation:
            return None

        if end_time < start_time:
            end_time = start_time

        parameters = instruction.get("parameters", {})
        if not isinstance(parameters, dict):
            parameters = {}

        return TimelineEvent(
            event_type=str(instruction_type),
            start_time=start_time,
            end_time=end_time,
            track=track,
            operation=operation,
            parameters=parameters,
            priority=str(instruction.get("priority") or "medium"),
            source_instruction_type=str(instruction_type),
            source_segment_id=instruction.get("source_segment_id"),
            reason=str(instruction.get("reason") or ""),
        )

    def normalize_many(
        self,
        instructions: list[dict[str, Any]],
    ) -> list[TimelineEvent]:
        events: list[TimelineEvent] = []

        for instruction in instructions:
            event = self.normalize(instruction)
            if event is not None:
                events.append(event)

        return events

    def _safe_float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0