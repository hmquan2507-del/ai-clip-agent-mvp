from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EditingStylePlan:
    subtitle_style: str
    caption_density: str
    camera_motion: str
    broll_strategy: str
    music_style: str
    sfx_style: str
    transition_style: str
    cut_speed: str
    highlight_strategy: str
    zoom_frequency: str
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "subtitle_style": self.subtitle_style,
            "caption_density": self.caption_density,
            "camera_motion": self.camera_motion,
            "broll_strategy": self.broll_strategy,
            "music_style": self.music_style,
            "sfx_style": self.sfx_style,
            "transition_style": self.transition_style,
            "cut_speed": self.cut_speed,
            "highlight_strategy": self.highlight_strategy,
            "zoom_frequency": self.zoom_frequency,
            "reasons": self.reasons,
        }


@dataclass
class EditingStyleResult:
    production_id: str
    style_profile: str
    editing_style: EditingStylePlan
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "style_profile": self.style_profile,
            "editing_style": self.editing_style.to_dict(),
            "metadata": self.metadata,
        }