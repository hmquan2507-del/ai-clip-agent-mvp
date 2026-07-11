from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.render.execution.quality.enums import (
    RenderQualityCheckStatus,
    RenderQualityCheckType,
    RenderQualityStatus,
)


@dataclass
class RenderQualityThresholds:
    duration_tolerance_seconds: float = 0.5

    expected_width: int | None = None
    expected_height: int | None = None
    expected_fps: float | None = None
    fps_tolerance: float = 0.5

    allowed_video_codecs: set[str] = field(
        default_factory=lambda: {
            "h264",
            "hevc",
            "vp9",
            "av1",
        }
    )

    allowed_audio_codecs: set[str] = field(
        default_factory=lambda: {
            "aac",
            "mp3",
            "opus",
            "vorbis",
        }
    )

    black_frame_min_duration: float = 1.0
    black_frame_picture_threshold: float = 0.98
    black_frame_pixel_threshold: float = 0.10

    silence_min_duration: float = 2.0
    silence_noise_threshold_db: float = -50.0

    max_black_ratio_warning: float = 0.10
    max_black_ratio_reject: float = 0.30

    max_silence_ratio_warning: float = 0.25
    max_silence_ratio_reject: float = 0.60

    minimum_quality_score: float = 70.0
    warning_quality_score: float = 85.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "duration_tolerance_seconds": (
                self.duration_tolerance_seconds
            ),
            "expected_width": self.expected_width,
            "expected_height": self.expected_height,
            "expected_fps": self.expected_fps,
            "fps_tolerance": self.fps_tolerance,
            "allowed_video_codecs": sorted(
                self.allowed_video_codecs
            ),
            "allowed_audio_codecs": sorted(
                self.allowed_audio_codecs
            ),
            "black_frame_min_duration": (
                self.black_frame_min_duration
            ),
            "black_frame_picture_threshold": (
                self.black_frame_picture_threshold
            ),
            "black_frame_pixel_threshold": (
                self.black_frame_pixel_threshold
            ),
            "silence_min_duration": (
                self.silence_min_duration
            ),
            "silence_noise_threshold_db": (
                self.silence_noise_threshold_db
            ),
            "max_black_ratio_warning": (
                self.max_black_ratio_warning
            ),
            "max_black_ratio_reject": (
                self.max_black_ratio_reject
            ),
            "max_silence_ratio_warning": (
                self.max_silence_ratio_warning
            ),
            "max_silence_ratio_reject": (
                self.max_silence_ratio_reject
            ),
            "minimum_quality_score": (
                self.minimum_quality_score
            ),
            "warning_quality_score": (
                self.warning_quality_score
            ),
        }


@dataclass
class RenderQualityInterval:
    start_time: float
    end_time: float
    duration: float
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "metadata": self.metadata,
        }


@dataclass
class RenderQualityCheck:
    check_type: RenderQualityCheckType | str
    status: RenderQualityCheckStatus | str
    score: float

    message: str
    expected: Any = None
    actual: Any = None

    intervals: list[RenderQualityInterval] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_type": self._value(
                self.check_type
            ),
            "status": self._value(self.status),
            "score": self.score,
            "message": self.message,
            "expected": self.expected,
            "actual": self.actual,
            "intervals": [
                item.to_dict()
                for item in self.intervals
            ],
            "metadata": self.metadata,
        }

    def _value(self, value: Any) -> str:
        return (
            value.value
            if hasattr(value, "value")
            else str(value)
        )


@dataclass
class RenderQualityReport:
    production_id: str
    output_path: str

    status: RenderQualityStatus | str
    quality_score: float

    checks: list[RenderQualityCheck]

    approved: bool
    warning_count: int
    failure_count: int

    report_path: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "output_path": self.output_path,
            "status": self._value(self.status),
            "quality_score": self.quality_score,
            "checks": [
                item.to_dict()
                for item in self.checks
            ],
            "approved": self.approved,
            "warning_count": self.warning_count,
            "failure_count": self.failure_count,
            "report_path": self.report_path,
            "metadata": self.metadata,
        }

    def _value(self, value: Any) -> str:
        return (
            value.value
            if hasattr(value, "value")
            else str(value)
        )