from __future__ import annotations

import json

from app.planner.models import PlannerContext, PlannerHint, PlannerSegment


class PlannerPromptBuilder:
    def build_asset_planner_prompt(
        self,
        context: PlannerContext,
        segments: list[PlannerSegment],
        hints: list[PlannerHint],
    ) -> str:
        payload = {
            "role": "AI Video Director",
            "task": "Create an editing asset plan for a short-form video.",
            "rules": [
                "Return JSON only.",
                "Do not download assets.",
                "Do not call providers.",
                "Only create planning instructions.",
                "Use broll, music, sound_effect, subtitle_style, font, motion, transition when useful.",
                "Every instruction must include start_time, end_time, reason, priority, and confidence.",
            ],
            "context": {
                "production_id": context.production_id,
                "platform": context.platform,
                "editing_style": context.editing_style,
                "story_type": context.story_type,
                "language": context.language,
                "metadata": context.metadata,
            },
            "segments": [
                {
                    "segment_id": segment.segment_id,
                    "start_time": segment.start_time,
                    "end_time": segment.end_time,
                    "duration": segment.duration,
                    "text": segment.text,
                    "segment_type": segment.segment_type,
                    "emotion": segment.emotion,
                    "importance_score": segment.importance_score,
                    "viral_potential_score": segment.viral_potential_score,
                    "metadata": segment.metadata,
                }
                for segment in segments
            ],
            "rule_hints": [
                {
                    "instruction_type": hint.instruction_type.value,
                    "query": hint.query,
                    "priority": hint.priority.value,
                    "reason": hint.reason,
                    "start_time": hint.start_time,
                    "end_time": hint.end_time,
                    "preferred_duration": hint.preferred_duration,
                    "preferred_orientation": hint.preferred_orientation,
                    "track_type": hint.track_type,
                    "layer": hint.layer,
                    "volume": hint.volume,
                    "opacity": hint.opacity,
                    "style_key": hint.style_key,
                    "font_family": hint.font_family,
                    "metadata": hint.metadata,
                }
                for hint in hints
            ],
            "expected_json_shape": {
                "planner_version": "1.0",
                "confidence": 0.9,
                "instructions": [
                    {
                        "instruction_type": "broll",
                        "query": "person editing video on laptop",
                        "start_time": 0,
                        "end_time": 4,
                        "priority": "critical",
                        "reason": "hook needs visual support",
                        "track_type": "broll",
                        "layer": 2,
                        "preferred_duration": 4,
                        "preferred_orientation": "portrait",
                        "confidence": 0.9,
                        "metadata": {},
                    }
                ],
            },
        }

        return json.dumps(payload, ensure_ascii=False, indent=2)