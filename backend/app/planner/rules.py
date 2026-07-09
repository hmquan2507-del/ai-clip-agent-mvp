from __future__ import annotations

from app.planner.models import (
    PlannerContext,
    PlannerHint,
    PlannerInstructionType,
    PlannerPriority,
    PlannerSegment,
)


class PlannerRuleEngine:
    def build_hints(
        self,
        context: PlannerContext,
        segments: list[PlannerSegment],
    ) -> list[PlannerHint]:
        hints: list[PlannerHint] = []

        hints.extend(self._global_style_hints(context))

        for segment in segments:
            hints.extend(self._segment_hints(context, segment))

        return hints

    def _global_style_hints(
        self,
        context: PlannerContext,
    ) -> list[PlannerHint]:
        hints: list[PlannerHint] = []

        if context.platform.lower() in {"tiktok", "reels", "shorts"}:
            hints.append(
                PlannerHint(
                    instruction_type=PlannerInstructionType.SUBTITLE_STYLE,
                    priority=PlannerPriority.HIGH,
                    reason="short form platform requires large readable subtitles",
                    style_key="tiktok_bold",
                    metadata={"platform": context.platform},
                )
            )

        if context.editing_style.lower() in {"viral", "high_energy"}:
            hints.append(
                PlannerHint(
                    instruction_type=PlannerInstructionType.FONT,
                    priority=PlannerPriority.HIGH,
                    reason="viral style benefits from bold high-contrast font",
                    font_family="Montserrat",
                    metadata={"editing_style": context.editing_style},
                )
            )
            hints.append(
                PlannerHint(
                    instruction_type=PlannerInstructionType.MUSIC,
                    query="corporate background music",
                    priority=PlannerPriority.MEDIUM,
                    reason="background music improves pacing for short-form edit",
                    track_type="music",
                    layer=1,
                    volume=0.18,
                    start_time=0.0,
                    end_time=self._estimate_total_duration(context),
                    metadata={"editing_style": context.editing_style},
                )
            )

        return hints

    def _segment_hints(
        self,
        context: PlannerContext,
        segment: PlannerSegment,
    ) -> list[PlannerHint]:
        hints: list[PlannerHint] = []

        if self._is_hook(segment):
            hints.extend(self._hook_hints(segment))

        if self._is_problem(segment):
            hints.extend(self._problem_hints(segment))

        if self._is_solution(segment):
            hints.extend(self._solution_hints(segment))

        if segment.emotion.lower() in {"excited", "surprised", "funny"}:
            hints.append(
                PlannerHint(
                    instruction_type=PlannerInstructionType.SOUND_EFFECT,
                    query="whoosh transition",
                    priority=PlannerPriority.HIGH,
                    reason="high emotion segment benefits from transition sound effect",
                    start_time=segment.start_time,
                    end_time=min(segment.start_time + 0.8, segment.end_time),
                    preferred_duration=0.8,
                    track_type="sfx",
                    layer=3,
                    volume=0.75,
                    metadata={"segment_id": segment.segment_id, "emotion": segment.emotion},
                )
            )

        if segment.importance_score >= 0.75:
            hints.append(
                PlannerHint(
                    instruction_type=PlannerInstructionType.SUBTITLE_STYLE,
                    priority=PlannerPriority.HIGH,
                    reason="important segment should use emphasized subtitle style",
                    start_time=segment.start_time,
                    end_time=segment.end_time,
                    style_key="hormozi",
                    metadata={"segment_id": segment.segment_id},
                )
            )

        return hints

    def _hook_hints(
        self,
        segment: PlannerSegment,
    ) -> list[PlannerHint]:
        return [
            PlannerHint(
                instruction_type=PlannerInstructionType.BROLL,
                query=self._broll_query(segment),
                priority=PlannerPriority.CRITICAL,
                reason="hook needs visual support to increase retention",
                start_time=segment.start_time,
                end_time=min(segment.end_time, segment.start_time + 4.0),
                preferred_duration=min(segment.duration, 4.0),
                preferred_orientation="portrait",
                track_type="broll",
                layer=2,
                opacity=1.0,
                metadata={"segment_id": segment.segment_id, "segment_type": segment.segment_type},
            ),
            PlannerHint(
                instruction_type=PlannerInstructionType.MOTION,
                query="zoom_in",
                priority=PlannerPriority.HIGH,
                reason="hook needs camera movement",
                start_time=segment.start_time,
                end_time=min(segment.end_time, segment.start_time + 2.0),
                metadata={"segment_id": segment.segment_id, "motion": "zoom_in"},
            ),
        ]

    def _problem_hints(
        self,
        segment: PlannerSegment,
    ) -> list[PlannerHint]:
        return [
            PlannerHint(
                instruction_type=PlannerInstructionType.BROLL,
                query="person stressed editing video on laptop",
                priority=PlannerPriority.HIGH,
                reason="problem segment needs pain-point b-roll",
                start_time=segment.start_time,
                end_time=min(segment.end_time, segment.start_time + 4.0),
                preferred_duration=min(segment.duration, 4.0),
                preferred_orientation="portrait",
                track_type="broll",
                layer=2,
                opacity=1.0,
                metadata={"segment_id": segment.segment_id, "segment_type": segment.segment_type},
            )
        ]

    def _solution_hints(
        self,
        segment: PlannerSegment,
    ) -> list[PlannerHint]:
        return [
            PlannerHint(
                instruction_type=PlannerInstructionType.BROLL,
                query="office worker using computer successful",
                priority=PlannerPriority.HIGH,
                reason="solution segment needs positive workflow b-roll",
                start_time=segment.start_time,
                end_time=min(segment.end_time, segment.start_time + 4.0),
                preferred_duration=min(segment.duration, 4.0),
                preferred_orientation="portrait",
                track_type="broll",
                layer=2,
                opacity=1.0,
                metadata={"segment_id": segment.segment_id, "segment_type": segment.segment_type},
            )
        ]

    def _is_hook(self, segment: PlannerSegment) -> bool:
        return (
            segment.segment_type.lower() == "hook"
            or segment.viral_potential_score >= 0.85
            or segment.start_time <= 3.0
        )

    def _is_problem(self, segment: PlannerSegment) -> bool:
        text = segment.text.lower()
        return (
            segment.segment_type.lower() in {"problem", "pain_point"}
            or "khó" in text
            or "mất thời gian" in text
            or "lãng phí" in text
            or "sai lầm" in text
        )

    def _is_solution(self, segment: PlannerSegment) -> bool:
        text = segment.text.lower()
        return (
            segment.segment_type.lower() in {"solution", "main_point"}
            or "giải pháp" in text
            or "tự động" in text
            or "ai" in text
        )

    def _broll_query(self, segment: PlannerSegment) -> str:
        text = segment.text.lower()

        if "edit" in text or "video" in text:
            return "person editing video on laptop"

        if "ai" in text:
            return "artificial intelligence technology interface"

        return "creator working on laptop"

    def _estimate_total_duration(self, context: PlannerContext) -> float:
        value = context.metadata.get("total_duration")

        if isinstance(value, (int, float)):
            return float(value)

        return 60.0