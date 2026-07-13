from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.review.preview.enums import (
    PreviewPlaybackStatus,
    PreviewSessionEventType,
)


def utc_now_iso() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


@dataclass(frozen=True)
class PreviewMediaSource:
    production_id: str

    video_path: str | None = None
    video_url: str | None = None

    duration: float = 0.0
    width: int | None = None
    height: int | None = None
    fps: float = 30.0

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "duration",
            max(
                0.0,
                float(self.duration),
            ),
        )

        normalized_fps = float(
            self.fps
        )

        if normalized_fps <= 0:
            normalized_fps = 30.0

        object.__setattr__(
            self,
            "fps",
            normalized_fps,
        )

    @property
    def available(self) -> bool:
        return bool(
            self.video_path
            or self.video_url
        )

    @property
    def frame_duration(self) -> float:
        return 1.0 / self.fps

    @property
    def total_frames(self) -> int:
        if self.duration <= 0:
            return 0

        return int(
            round(
                self.duration
                * self.fps
            )
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": (
                self.production_id
            ),
            "video_path": self.video_path,
            "video_url": self.video_url,
            "available": self.available,
            "duration": self.duration,
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "frame_duration": (
                self.frame_duration
            ),
            "total_frames": (
                self.total_frames
            ),
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class PreviewSessionConfig:
    initial_volume: float = 1.0
    initial_playback_rate: float = 1.0
    initial_zoom: float = 1.0

    min_playback_rate: float = 0.25
    max_playback_rate: float = 4.0

    min_zoom: float = 0.25
    max_zoom: float = 4.0

    loop_enabled: bool = False
    auto_pause_at_end: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "initial_volume",
            min(
                1.0,
                max(
                    0.0,
                    float(
                        self.initial_volume
                    ),
                ),
            ),
        )

        min_rate = max(
            0.01,
            float(
                self.min_playback_rate
            ),
        )

        max_rate = max(
            min_rate,
            float(
                self.max_playback_rate
            ),
        )

        object.__setattr__(
            self,
            "min_playback_rate",
            min_rate,
        )
        object.__setattr__(
            self,
            "max_playback_rate",
            max_rate,
        )

        initial_rate = min(
            max_rate,
            max(
                min_rate,
                float(
                    self.initial_playback_rate
                ),
            ),
        )

        object.__setattr__(
            self,
            "initial_playback_rate",
            initial_rate,
        )

        min_zoom = max(
            0.01,
            float(self.min_zoom),
        )

        max_zoom = max(
            min_zoom,
            float(self.max_zoom),
        )

        object.__setattr__(
            self,
            "min_zoom",
            min_zoom,
        )
        object.__setattr__(
            self,
            "max_zoom",
            max_zoom,
        )

        initial_zoom = min(
            max_zoom,
            max(
                min_zoom,
                float(
                    self.initial_zoom
                ),
            ),
        )

        object.__setattr__(
            self,
            "initial_zoom",
            initial_zoom,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "initial_volume": (
                self.initial_volume
            ),
            "initial_playback_rate": (
                self.initial_playback_rate
            ),
            "initial_zoom": (
                self.initial_zoom
            ),
            "min_playback_rate": (
                self.min_playback_rate
            ),
            "max_playback_rate": (
                self.max_playback_rate
            ),
            "min_zoom": self.min_zoom,
            "max_zoom": self.max_zoom,
            "loop_enabled": (
                self.loop_enabled
            ),
            "auto_pause_at_end": (
                self.auto_pause_at_end
            ),
        }


@dataclass
class PreviewSessionState:
    production_id: str

    status: PreviewPlaybackStatus = (
        PreviewPlaybackStatus.IDLE
    )

    current_time: float = 0.0
    duration: float = 0.0

    volume: float = 1.0
    muted: bool = False

    playback_rate: float = 1.0
    zoom: float = 1.0

    loop_enabled: bool = False

    current_frame: int = 0
    total_frames: int = 0

    revision: int = 1

    created_at: str = field(
        default_factory=utc_now_iso
    )
    updated_at: str = field(
        default_factory=utc_now_iso
    )

    error: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def playing(self) -> bool:
        return (
            self.status
            == PreviewPlaybackStatus.PLAYING
        )

    @property
    def progress(self) -> float:
        if self.duration <= 0:
            return 0.0

        return min(
            100.0,
            max(
                0.0,
                (
                    self.current_time
                    / self.duration
                )
                * 100.0,
            ),
        )

    @property
    def effective_volume(self) -> float:
        if self.muted:
            return 0.0

        return self.volume

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": (
                self.production_id
            ),
            "status": self.status.value,
            "playing": self.playing,
            "current_time": (
                self.current_time
            ),
            "duration": self.duration,
            "progress": self.progress,
            "volume": self.volume,
            "muted": self.muted,
            "effective_volume": (
                self.effective_volume
            ),
            "playback_rate": (
                self.playback_rate
            ),
            "zoom": self.zoom,
            "loop_enabled": (
                self.loop_enabled
            ),
            "current_frame": (
                self.current_frame
            ),
            "total_frames": (
                self.total_frames
            ),
            "revision": self.revision,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "error": self.error,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class PreviewSessionEvent:
    event_type: PreviewSessionEventType
    production_id: str

    state_revision: int
    current_time: float

    created_at: str = field(
        default_factory=utc_now_iso
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": (
                self.event_type.value
            ),
            "production_id": (
                self.production_id
            ),
            "state_revision": (
                self.state_revision
            ),
            "current_time": (
                self.current_time
            ),
            "created_at": (
                self.created_at
            ),
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class PreviewSessionResult:
    success: bool
    state: PreviewSessionState

    event: PreviewSessionEvent | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "state": self.state.to_dict(),
            "event": (
                self.event.to_dict()
                if self.event
                else None
            ),
            "error": self.error,
        }