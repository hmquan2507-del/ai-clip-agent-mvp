from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MediaValidationResult:
    local_path: str
    valid: bool
    duration: float | None = None
    width: int | None = None
    height: int | None = None
    fps: float | None = None
    video_codec: str | None = None
    audio_codec: str | None = None
    has_video: bool = False
    has_audio: bool = False
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "local_path": self.local_path,
            "valid": self.valid,
            "duration": self.duration,
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "video_codec": self.video_codec,
            "audio_codec": self.audio_codec,
            "has_video": self.has_video,
            "has_audio": self.has_audio,
            "errors": self.errors,
            "metadata": self.metadata,
        }