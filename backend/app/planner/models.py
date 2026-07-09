from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PlannerInstructionType(str, Enum):
    BROLL = "broll"
    MUSIC = "music"
    SOUND_EFFECT = "sound_effect"
    SUBTITLE_STYLE = "subtitle_style"
    FONT = "font"
    MOTION = "motion"
    TRANSITION = "transition"
    CTA = "cta"
    STICKER = "sticker"


class PlannerPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PlannerSegment:
    segment_id: str
    start_time: float
    end_time: float
    text: str
    segment_type: str = "main_point"
    emotion: str = "neutral"
    importance_score: float = 0.5
    viral_potential_score: float = 0.5
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        return max(0.0, self.end_time - self.start_time)


@dataclass
class PlannerContext:
    production_id: str
    platform: str = "tiktok"
    editing_style: str = "viral"
    story_type: str = "problem_solution"
    language: str = "vi"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PlannerHint:
    instruction_type: PlannerInstructionType
    query: str | None = None
    priority: PlannerPriority = PlannerPriority.MEDIUM
    reason: str = ""
    start_time: float | None = None
    end_time: float | None = None
    preferred_duration: float | None = None
    preferred_orientation: str | None = None
    track_type: str | None = None
    layer: int = 1
    volume: float | None = None
    opacity: float | None = None
    style_key: str | None = None
    font_family: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PlannerInstruction:
    instruction_type: PlannerInstructionType
    query: str | None
    start_time: float
    end_time: float
    priority: PlannerPriority
    reason: str
    track_type: str | None = None
    layer: int = 1
    preferred_duration: float | None = None
    preferred_orientation: str | None = None
    volume: float | None = None
    opacity: float | None = None
    style_key: str | None = None
    font_family: str | None = None
    confidence: float = 0.8
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        return max(0.0, self.end_time - self.start_time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "instruction_type": self.instruction_type.value,
            "query": self.query,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "priority": self.priority.value,
            "reason": self.reason,
            "track_type": self.track_type,
            "layer": self.layer,
            "preferred_duration": self.preferred_duration,
            "preferred_orientation": self.preferred_orientation,
            "volume": self.volume,
            "opacity": self.opacity,
            "style_key": self.style_key,
            "font_family": self.font_family,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


@dataclass
class PlannerRequest:
    context: PlannerContext
    segments: list[PlannerSegment]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EditingPlan:
    production_id: str
    planner_version: str
    instructions: list[PlannerInstruction]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "planner_version": self.planner_version,
            "instructions": [item.to_dict() for item in self.instructions],
            "metadata": self.metadata,
        }