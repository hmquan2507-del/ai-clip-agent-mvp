from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable

from app.review.preview.enums import (
    PreviewPlaybackStatus,
    PreviewSessionEventType,
)
from app.review.preview.models import (
    PreviewMediaSource,
    PreviewSessionConfig,
    PreviewSessionEvent,
    PreviewSessionResult,
    PreviewSessionState,
    utc_now_iso,
)


PreviewEventCallback = Callable[
    [PreviewSessionEvent],
    None,
]


class PreviewSessionRuntime:
    def __init__(
        self,
        source: PreviewMediaSource,
        config: PreviewSessionConfig | None = None,
        event_callback: (
            PreviewEventCallback | None
        ) = None,
    ):
        self.source = source

        self.config = (
            config
            or PreviewSessionConfig()
        )

        self.event_callback = (
            event_callback
        )

        initial_status = (
            PreviewPlaybackStatus.READY
            if source.available
            else PreviewPlaybackStatus.IDLE
        )

        self._state = PreviewSessionState(
            production_id=(
                source.production_id
            ),
            status=initial_status,
            current_time=0.0,
            duration=source.duration,
            volume=(
                self.config.initial_volume
            ),
            muted=False,
            playback_rate=(
                self.config
                .initial_playback_rate
            ),
            zoom=(
                self.config.initial_zoom
            ),
            loop_enabled=(
                self.config.loop_enabled
            ),
            current_frame=0,
            total_frames=(
                source.total_frames
            ),
            metadata={
                "runtime": (
                    "PreviewSessionRuntime"
                ),
                "source_available": (
                    source.available
                ),
            },
        )

        self._initial_state = deepcopy(
            self._state
        )

        self._events: list[
            PreviewSessionEvent
        ] = []

        self._emit(
            PreviewSessionEventType
            .SESSION_CREATED,
            metadata={
                "source_available": (
                    source.available
                ),
            },
        )

        if source.available:
            self._emit(
                PreviewSessionEventType
                .SESSION_READY,
            )

    @property
    def state(
        self,
    ) -> PreviewSessionState:
        return deepcopy(
            self._state
        )

    @property
    def events(
        self,
    ) -> list[PreviewSessionEvent]:
        return list(
            self._events
        )

    def play(
        self,
    ) -> PreviewSessionResult:
        if not self.source.available:
            return self._fail(
                "Preview video is unavailable."
            )

        if self._state.duration <= 0:
            return self._fail(
                "Preview duration is invalid."
            )

        if (
            self._state.current_time
            >= self._state.duration
        ):
            if self._state.loop_enabled:
                self._set_position(
                    0.0
                )
            else:
                self._set_position(
                    0.0
                )

        self._state.status = (
            PreviewPlaybackStatus.PLAYING
        )

        self._touch()

        event = self._emit(
            PreviewSessionEventType
            .PLAYBACK_STARTED,
        )

        return self._success(
            event
        )

    def pause(
        self,
    ) -> PreviewSessionResult:
        if (
            self._state.status
            == PreviewPlaybackStatus.ERROR
        ):
            return self._fail(
                self._state.error
                or "Preview session has failed."
            )

        self._state.status = (
            PreviewPlaybackStatus.PAUSED
        )

        self._touch()

        event = self._emit(
            PreviewSessionEventType
            .PLAYBACK_PAUSED,
        )

        return self._success(
            event
        )

    def toggle_playback(
        self,
    ) -> PreviewSessionResult:
        if self._state.playing:
            return self.pause()

        return self.play()

    def seek(
        self,
        seconds: float,
    ) -> PreviewSessionResult:
        position = self._clamp_time(
            seconds
        )

        self._set_position(
            position
        )

        if (
            self._state.duration > 0
            and position
            >= self._state.duration
        ):
            self._state.status = (
                PreviewPlaybackStatus.ENDED
            )

        elif (
            self._state.status
            == PreviewPlaybackStatus.ENDED
        ):
            self._state.status = (
                PreviewPlaybackStatus.PAUSED
            )

        self._touch()

        event = self._emit(
            PreviewSessionEventType
            .POSITION_CHANGED,
            metadata={
                "position": position,
            },
        )

        return self._success(
            event
        )

    def seek_relative(
        self,
        delta_seconds: float,
    ) -> PreviewSessionResult:
        return self.seek(
            self._state.current_time
            + float(delta_seconds)
        )

    def set_volume(
        self,
        volume: float,
    ) -> PreviewSessionResult:
        normalized = min(
            1.0,
            max(
                0.0,
                float(volume),
            ),
        )

        self._state.volume = (
            normalized
        )

        self._touch()

        event = self._emit(
            PreviewSessionEventType
            .VOLUME_CHANGED,
            metadata={
                "volume": normalized,
            },
        )

        return self._success(
            event
        )

    def set_muted(
        self,
        muted: bool,
    ) -> PreviewSessionResult:
        self._state.muted = bool(
            muted
        )

        self._touch()

        event = self._emit(
            PreviewSessionEventType
            .MUTE_CHANGED,
            metadata={
                "muted": (
                    self._state.muted
                ),
            },
        )

        return self._success(
            event
        )

    def toggle_muted(
        self,
    ) -> PreviewSessionResult:
        return self.set_muted(
            not self._state.muted
        )

    def set_playback_rate(
        self,
        playback_rate: float,
    ) -> PreviewSessionResult:
        normalized = min(
            self.config.max_playback_rate,
            max(
                self.config.min_playback_rate,
                float(playback_rate),
            ),
        )

        self._state.playback_rate = (
            normalized
        )

        self._touch()

        event = self._emit(
            PreviewSessionEventType
            .PLAYBACK_RATE_CHANGED,
            metadata={
                "playback_rate": (
                    normalized
                ),
            },
        )

        return self._success(
            event
        )

    def set_zoom(
        self,
        zoom: float,
    ) -> PreviewSessionResult:
        normalized = min(
            self.config.max_zoom,
            max(
                self.config.min_zoom,
                float(zoom),
            ),
        )

        self._state.zoom = normalized

        self._touch()

        event = self._emit(
            PreviewSessionEventType
            .ZOOM_CHANGED,
            metadata={
                "zoom": normalized,
            },
        )

        return self._success(
            event
        )

    def set_loop_enabled(
        self,
        enabled: bool,
    ) -> PreviewSessionResult:
        self._state.loop_enabled = bool(
            enabled
        )

        self._touch()

        event = self._emit(
            PreviewSessionEventType
            .LOOP_CHANGED,
            metadata={
                "loop_enabled": (
                    self._state
                    .loop_enabled
                ),
            },
        )

        return self._success(
            event
        )

    def toggle_loop(
        self,
    ) -> PreviewSessionResult:
        return self.set_loop_enabled(
            not self._state.loop_enabled
        )

    def step_forward_frame(
        self,
        frame_count: int = 1,
    ) -> PreviewSessionResult:
        frames = max(
            1,
            int(frame_count),
        )

        self._state.status = (
            PreviewPlaybackStatus.PAUSED
        )

        result = self.seek_relative(
            self.source.frame_duration
            * frames
        )

        event = self._emit(
            PreviewSessionEventType
            .FRAME_STEPPED,
            metadata={
                "direction": "forward",
                "frame_count": frames,
                "current_frame": (
                    self._state
                    .current_frame
                ),
            },
        )

        return PreviewSessionResult(
            success=result.success,
            state=self.state,
            event=event,
            error=result.error,
        )

    def step_backward_frame(
        self,
        frame_count: int = 1,
    ) -> PreviewSessionResult:
        frames = max(
            1,
            int(frame_count),
        )

        self._state.status = (
            PreviewPlaybackStatus.PAUSED
        )

        result = self.seek_relative(
            -self.source.frame_duration
            * frames
        )

        event = self._emit(
            PreviewSessionEventType
            .FRAME_STEPPED,
            metadata={
                "direction": "backward",
                "frame_count": frames,
                "current_frame": (
                    self._state
                    .current_frame
                ),
            },
        )

        return PreviewSessionResult(
            success=result.success,
            state=self.state,
            event=event,
            error=result.error,
        )

    def tick(
        self,
        elapsed_seconds: float,
    ) -> PreviewSessionResult:
        if not self._state.playing:
            return self._success()

        elapsed = max(
            0.0,
            float(elapsed_seconds),
        )

        movement = (
            elapsed
            * self._state.playback_rate
        )

        target = (
            self._state.current_time
            + movement
        )

        if (
            self._state.duration > 0
            and target
            >= self._state.duration
        ):
            if self._state.loop_enabled:
                overflow = (
                    target
                    % self._state.duration
                )

                self._set_position(
                    overflow
                )

                self._touch()

                event = self._emit(
                    PreviewSessionEventType
                    .POSITION_CHANGED,
                    metadata={
                        "looped": True,
                        "position": overflow,
                    },
                )

                return self._success(
                    event
                )

            self._set_position(
                self._state.duration
            )

            self._state.status = (
                PreviewPlaybackStatus.ENDED
            )

            self._touch()

            event = self._emit(
                PreviewSessionEventType
                .PLAYBACK_ENDED,
            )

            return self._success(
                event
            )

        self._set_position(
            target
        )

        self._touch()

        event = self._emit(
            PreviewSessionEventType
            .POSITION_CHANGED,
            metadata={
                "tick": elapsed,
                "position": target,
            },
        )

        return self._success(
            event
        )

    def reset(
        self,
    ) -> PreviewSessionResult:
        created_at = (
            self._state.created_at
        )

        self._state = deepcopy(
            self._initial_state
        )

        self._state.created_at = (
            created_at
        )

        self._state.revision += 1
        self._state.updated_at = (
            utc_now_iso()
        )

        event = self._emit(
            PreviewSessionEventType
            .SESSION_RESET,
        )

        return self._success(
            event
        )

    def clear_events(
        self,
    ) -> None:
        self._events.clear()

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "source": (
                self.source.to_dict()
            ),
            "config": (
                self.config.to_dict()
            ),
            "state": (
                self._state.to_dict()
            ),
            "events": [
                event.to_dict()
                for event in self._events
            ],
            "metadata": {
                "runtime": (
                    "PreviewSessionRuntime"
                ),
                "event_count": len(
                    self._events
                ),
            },
        }

    def _set_position(
        self,
        seconds: float,
    ) -> None:
        position = self._clamp_time(
            seconds
        )

        self._state.current_time = (
            position
        )

        if self.source.fps > 0:
            frame = int(
                round(
                    position
                    * self.source.fps
                )
            )
        else:
            frame = 0

        if (
            self._state.total_frames
            > 0
        ):
            frame = min(
                self._state.total_frames,
                max(
                    0,
                    frame,
                ),
            )

        self._state.current_frame = (
            frame
        )

    def _clamp_time(
        self,
        seconds: float,
    ) -> float:
        value = max(
            0.0,
            float(seconds),
        )

        if self._state.duration <= 0:
            return 0.0

        return min(
            self._state.duration,
            value,
        )

    def _touch(
        self,
    ) -> None:
        self._state.revision += 1
        self._state.updated_at = (
            utc_now_iso()
        )
        self._state.error = None

    def _emit(
        self,
        event_type: PreviewSessionEventType,
        *,
        metadata: dict[str, Any]
        | None = None,
    ) -> PreviewSessionEvent:
        event = PreviewSessionEvent(
            event_type=event_type,
            production_id=(
                self._state
                .production_id
            ),
            state_revision=(
                self._state.revision
            ),
            current_time=(
                self._state.current_time
            ),
            metadata=dict(
                metadata or {}
            ),
        )

        self._events.append(
            event
        )

        if self.event_callback:
            self.event_callback(
                event
            )

        return event

    def _success(
        self,
        event: PreviewSessionEvent
        | None = None,
    ) -> PreviewSessionResult:
        return PreviewSessionResult(
            success=True,
            state=self.state,
            event=event,
            error=None,
        )

    def _fail(
        self,
        message: str,
    ) -> PreviewSessionResult:
        self._state.status = (
            PreviewPlaybackStatus.ERROR
        )
        self._state.error = message

        self._touch()

        self._state.error = message

        event = self._emit(
            PreviewSessionEventType
            .SESSION_ERROR,
            metadata={
                "error": message,
            },
        )

        return PreviewSessionResult(
            success=False,
            state=self.state,
            event=event,
            error=message,
        )