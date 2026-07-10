from __future__ import annotations

import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from app.media.validation import (
    MediaValidationRuntime,
)
from app.render.ffmpeg.execution.models import (
    FFmpegCommand,
    FFmpegExecutionIssue,
    FFmpegExecutionResult,
    FFmpegProgressEvent,
)


ProgressCallback = Callable[
    [FFmpegProgressEvent],
    None,
]


class FFmpegCommandExecutor:
    def __init__(
        self,
        media_validator: MediaValidationRuntime | None = None,
        timeout_seconds: int = 1800,
        stderr_tail_lines: int = 80,
    ):
        self.media_validator = (
            media_validator
            or MediaValidationRuntime()
        )
        self.timeout_seconds = timeout_seconds
        self.stderr_tail_lines = max(
            1,
            stderr_tail_lines,
        )

    def execute(
        self,
        production_id: str,
        command: FFmpegCommand,
        progress_callback: ProgressCallback | None = None,
    ) -> FFmpegExecutionResult:
        started_at = self._now()
        started_counter = time.perf_counter()

        progress_events: list[
            FFmpegProgressEvent
        ] = []
        issues: list[
            FFmpegExecutionIssue
        ] = []

        output_path = Path(
            command.output_path
        )
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if output_path.exists():
            output_path.unlink()

        process: subprocess.Popen[str] | None = None
        returncode: int | None = None
        stderr_text = ""

        try:
            process = subprocess.Popen(
                command.as_list(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )

            if process.stdout is None:
                raise RuntimeError(
                    "FFmpeg stdout pipe is unavailable."
                )

            current_payload: dict[str, str] = {}

            while True:
                if (
                    time.perf_counter()
                    - started_counter
                    > self.timeout_seconds
                ):
                    process.kill()

                    issues.append(
                        FFmpegExecutionIssue(
                            level="error",
                            code="ffmpeg_timeout",
                            message=(
                                "FFmpeg execution exceeded "
                                "the configured timeout."
                            ),
                            metadata={
                                "timeout_seconds": (
                                    self.timeout_seconds
                                ),
                            },
                        )
                    )

                    break

                line = process.stdout.readline()

                if line:
                    line = line.strip()

                    if "=" in line:
                        key, value = line.split(
                            "=",
                            1,
                        )
                        current_payload[key] = value

                    if line.startswith("progress="):
                        event = (
                            self._progress_event_from_payload(
                                payload=current_payload,
                                duration=command.duration,
                            )
                        )

                        progress_events.append(
                            event
                        )

                        if progress_callback:
                            progress_callback(
                                event
                            )

                        current_payload = {}

                if line == "" and process.poll() is not None:
                    break

            returncode = process.wait()

            if process.stderr is not None:
                stderr_text = (
                    process.stderr.read()
                    or ""
                )

        except FileNotFoundError:
            issues.append(
                FFmpegExecutionIssue(
                    level="error",
                    code="ffmpeg_not_installed",
                    message=(
                        "FFmpeg executable was not found."
                    ),
                    metadata={
                        "binary": command.binary,
                    },
                )
            )

        except Exception as error:
            issues.append(
                FFmpegExecutionIssue(
                    level="error",
                    code="ffmpeg_execution_exception",
                    message=str(error),
                )
            )

            if process is not None:
                try:
                    process.kill()
                except Exception:
                    pass

        if returncode not in {
            None,
            0,
        }:
            issues.append(
                FFmpegExecutionIssue(
                    level="error",
                    code="ffmpeg_nonzero_exit",
                    message=(
                        "FFmpeg returned a non-zero "
                        "exit code."
                    ),
                    metadata={
                        "returncode": returncode,
                    },
                )
            )

        output_validation = None

        if (
            returncode == 0
            and output_path.exists()
        ):
            output_validation = (
                self.media_validator.validate(
                    local_path=str(
                        output_path
                    ),
                    require_video=True,
                )
            )

            if not output_validation.valid:
                issues.append(
                    FFmpegExecutionIssue(
                        level="error",
                        code="render_output_invalid",
                        message=(
                            "Rendered output failed "
                            "media validation."
                        ),
                        metadata=(
                            output_validation.to_dict()
                        ),
                    )
                )
        elif returncode == 0:
            issues.append(
                FFmpegExecutionIssue(
                    level="error",
                    code="render_output_missing",
                    message=(
                        "FFmpeg completed but output "
                        "file was not created."
                    ),
                    metadata={
                        "output_path": (
                            str(output_path)
                        ),
                    },
                )
            )

        success = (
            returncode == 0
            and output_validation is not None
            and output_validation.valid
            and not any(
                issue.level == "error"
                for issue in issues
            )
        )

        duration_seconds = round(
            time.perf_counter()
            - started_counter,
            6,
        )

        if success and (
            not progress_events
            or progress_events[-1].progress
            < 100.0
        ):
            final_event = FFmpegProgressEvent(
                progress=100.0,
                out_time_seconds=(
                    output_validation.duration
                    or command.duration
                    or 0.0
                ),
                status="end",
                metadata={
                    "synthetic_final_event": True,
                },
            )

            progress_events.append(
                final_event
            )

            if progress_callback:
                progress_callback(
                    final_event
                )

        finished_at = self._now()

        return FFmpegExecutionResult(
            production_id=production_id,
            success=success,
            returncode=returncode,
            output_path=str(output_path),
            command=command,
            started_at=started_at,
            finished_at=finished_at,
            duration_seconds=duration_seconds,
            progress_events=progress_events,
            issues=issues,
            stderr_tail=self._stderr_tail(
                stderr_text
            ),
            output_file_size=(
                output_path.stat().st_size
                if output_path.exists()
                else None
            ),
            output_duration=(
                output_validation.duration
                if output_validation
                else None
            ),
            output_width=(
                output_validation.width
                if output_validation
                else None
            ),
            output_height=(
                output_validation.height
                if output_validation
                else None
            ),
            output_fps=(
                output_validation.fps
                if output_validation
                else None
            ),
            output_video_codec=(
                output_validation.video_codec
                if output_validation
                else None
            ),
            output_audio_codec=(
                output_validation.audio_codec
                if output_validation
                else None
            ),
            metadata={
                "executor": (
                    "FFmpegCommandExecutor"
                ),
                "progress_event_count": len(
                    progress_events
                ),
                "timeout_seconds": (
                    self.timeout_seconds
                ),
            },
        )

    def write_report(
        self,
        result: FFmpegExecutionResult,
        report_path: str,
    ) -> str:
        path = Path(report_path)
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            json.dumps(
                result.to_dict(),
                ensure_ascii=False,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )

        return str(path)

    def _progress_event_from_payload(
        self,
        payload: dict[str, str],
        duration: float,
    ) -> FFmpegProgressEvent:
        out_time_seconds = (
            self._parse_out_time(payload)
        )

        progress = 0.0

        if duration > 0:
            progress = min(
                100.0,
                max(
                    0.0,
                    out_time_seconds
                    / duration
                    * 100.0,
                ),
            )

        if payload.get("progress") == "end":
            progress = 100.0

        return FFmpegProgressEvent(
            progress=round(
                progress,
                2,
            ),
            out_time_seconds=round(
                out_time_seconds,
                3,
            ),
            speed=payload.get("speed"),
            frame=self._int_or_none(
                payload.get("frame")
            ),
            fps=self._float_or_none(
                payload.get("fps")
            ),
            bitrate=payload.get("bitrate"),
            total_size=self._int_or_none(
                payload.get("total_size")
            ),
            status=payload.get("progress"),
            metadata={
                "raw": dict(payload),
            },
        )

    def _parse_out_time(
        self,
        payload: dict[str, str],
    ) -> float:
        out_time_us = payload.get(
            "out_time_us"
        )

        if out_time_us is not None:
            try:
                return float(
                    out_time_us
                ) / 1_000_000.0
            except (TypeError, ValueError):
                pass

        out_time_ms = payload.get(
            "out_time_ms"
        )

        if out_time_ms is not None:
            try:
                value = float(
                    out_time_ms
                )

                if value > 100_000:
                    return value / 1_000_000.0

                return value / 1000.0

            except (TypeError, ValueError):
                pass

        out_time = payload.get(
            "out_time"
        )

        if out_time:
            return self._parse_timestamp(
                out_time
            )

        return 0.0

    def _parse_timestamp(
        self,
        value: str,
    ) -> float:
        try:
            hours, minutes, seconds = (
                value.split(":", 2)
            )

            return (
                float(hours) * 3600
                + float(minutes) * 60
                + float(seconds)
            )
        except (
            ValueError,
            AttributeError,
        ):
            return 0.0

    def _stderr_tail(
        self,
        value: str,
    ) -> str | None:
        if not value:
            return None

        lines = value.splitlines()

        return "\n".join(
            lines[
                -self.stderr_tail_lines:
            ]
        )

    def _int_or_none(
        self,
        value: str | None,
    ) -> int | None:
        if value is None:
            return None

        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _float_or_none(
        self,
        value: str | None,
    ) -> float | None:
        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _now(self) -> str:
        return datetime.now(
            timezone.utc
        ).isoformat()