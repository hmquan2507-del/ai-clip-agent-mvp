from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

from app.media.validation import (
    MediaValidationRuntime,
)
from app.render.execution.context import (
    RenderContext,
)
from app.render.execution.quality.enums import (
    RenderQualityCheckStatus,
    RenderQualityCheckType,
    RenderQualityStatus,
)
from app.render.execution.quality.models import (
    RenderQualityCheck,
    RenderQualityInterval,
    RenderQualityReport,
    RenderQualityThresholds,
)


class RenderQualityGate:
    def __init__(
        self,
        media_validator: MediaValidationRuntime | None = None,
        ffmpeg_binary: str = "ffmpeg",
        timeout_seconds: int = 300,
    ):
        self.media_validator = (
            media_validator
            or MediaValidationRuntime()
        )
        self.ffmpeg_binary = ffmpeg_binary
        self.timeout_seconds = timeout_seconds

    def validate(
        self,
        context: RenderContext,
        output_path: str,
        thresholds: RenderQualityThresholds | None = None,
    ) -> RenderQualityReport:
        thresholds = (
            thresholds
            or RenderQualityThresholds(
                expected_width=(
                    context.render_config.width
                ),
                expected_height=(
                    context.render_config.height
                ),
                expected_fps=(
                    context.render_config.fps
                ),
            )
        )

        path = Path(output_path)
        checks: list[RenderQualityCheck] = []

        media_result = self.media_validator.validate(
            local_path=str(path),
            require_video=True,
        )

        checks.append(
            self._media_validation_check(
                media_result
            )
        )

        checks.append(
            self._file_integrity_check(path)
        )

        if media_result.valid:
            checks.extend(
                [
                    self._duration_check(
                        actual=media_result.duration,
                        expected=(
                            context
                            .execution_timeline
                            .duration
                        ),
                        thresholds=thresholds,
                    ),
                    self._resolution_check(
                        width=media_result.width,
                        height=media_result.height,
                        thresholds=thresholds,
                    ),
                    self._fps_check(
                        actual=media_result.fps,
                        thresholds=thresholds,
                    ),
                    self._video_codec_check(
                        codec=media_result.video_codec,
                        thresholds=thresholds,
                    ),
                    self._audio_codec_check(
                        codec=media_result.audio_codec,
                        has_audio=media_result.has_audio,
                        thresholds=thresholds,
                    ),
                ]
            )

            checks.append(
                self._black_frame_check(
                    path=path,
                    duration=(
                        media_result.duration or 0.0
                    ),
                    thresholds=thresholds,
                )
            )

            checks.append(
                self._silence_check(
                    path=path,
                    duration=(
                        media_result.duration or 0.0
                    ),
                    has_audio=media_result.has_audio,
                    thresholds=thresholds,
                )
            )
        else:
            checks.extend(
                self._skipped_media_checks()
            )

        checks.append(
            self._artifact_integrity_check(
                context=context,
                output_path=path,
            )
        )

        quality_score = self._quality_score(
            checks
        )

        failure_count = sum(
            1
            for check in checks
            if self._value(check.status)
            == RenderQualityCheckStatus.FAIL.value
        )

        warning_count = sum(
            1
            for check in checks
            if self._value(check.status)
            == RenderQualityCheckStatus.WARNING.value
        )

        if (
            failure_count > 0
            or quality_score
            < thresholds.minimum_quality_score
        ):
            status = RenderQualityStatus.REJECTED
        elif (
            warning_count > 0
            or quality_score
            < thresholds.warning_quality_score
        ):
            status = RenderQualityStatus.WARNING
        else:
            status = RenderQualityStatus.APPROVED

        report = RenderQualityReport(
            production_id=context.production_id,
            output_path=str(path),
            status=status,
            quality_score=quality_score,
            checks=checks,
            approved=(
                status
                != RenderQualityStatus.REJECTED
            ),
            warning_count=warning_count,
            failure_count=failure_count,
            metadata={
                "runtime": "RenderQualityGate",
                "thresholds": thresholds.to_dict(),
                "check_count": len(checks),
            },
        )

        report_path = (
            Path(context.artifact_directory)
            / "render_quality_report.json"
        )

        report.report_path = str(report_path)

        report_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        report_path.write_text(
            json.dumps(
                report.to_dict(),
                ensure_ascii=False,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )

        context.metadata = {
            **context.metadata,
            "render_quality_status": (
                self._value(status)
            ),
            "render_quality_score": (
                quality_score
            ),
            "render_quality_report": (
                str(report_path)
            ),
            "render_quality_approved": (
                report.approved
            ),
        }

        return report

    def _media_validation_check(
        self,
        result,
    ) -> RenderQualityCheck:
        if result.valid:
            return RenderQualityCheck(
                check_type=(
                    RenderQualityCheckType
                    .MEDIA_VALIDATION
                ),
                status=(
                    RenderQualityCheckStatus.PASS
                ),
                score=100.0,
                message=(
                    "Output passed media validation."
                ),
                actual=result.to_dict(),
            )

        return RenderQualityCheck(
            check_type=(
                RenderQualityCheckType
                .MEDIA_VALIDATION
            ),
            status=RenderQualityCheckStatus.FAIL,
            score=0.0,
            message=(
                "Output failed media validation."
            ),
            actual=result.to_dict(),
        )

    def _file_integrity_check(
        self,
        path: Path,
    ) -> RenderQualityCheck:
        if not path.exists():
            return RenderQualityCheck(
                check_type=(
                    RenderQualityCheckType
                    .FILE_INTEGRITY
                ),
                status=RenderQualityCheckStatus.FAIL,
                score=0.0,
                message="Output file does not exist.",
                actual=str(path),
            )

        if not path.is_file():
            return RenderQualityCheck(
                check_type=(
                    RenderQualityCheckType
                    .FILE_INTEGRITY
                ),
                status=RenderQualityCheckStatus.FAIL,
                score=0.0,
                message=(
                    "Output path is not a file."
                ),
                actual=str(path),
            )

        size = path.stat().st_size

        if size <= 0:
            return RenderQualityCheck(
                check_type=(
                    RenderQualityCheckType
                    .FILE_INTEGRITY
                ),
                status=RenderQualityCheckStatus.FAIL,
                score=0.0,
                message="Output file is empty.",
                actual=size,
            )

        return RenderQualityCheck(
            check_type=(
                RenderQualityCheckType
                .FILE_INTEGRITY
            ),
            status=RenderQualityCheckStatus.PASS,
            score=100.0,
            message="Output file integrity passed.",
            actual={
                "file_size": size,
                "checksum": self._checksum(path),
            },
        )

    def _duration_check(
        self,
        actual: float | None,
        expected: float,
        thresholds: RenderQualityThresholds,
    ) -> RenderQualityCheck:
        if actual is None:
            return RenderQualityCheck(
                check_type=(
                    RenderQualityCheckType.DURATION
                ),
                status=RenderQualityCheckStatus.FAIL,
                score=0.0,
                message=(
                    "Output duration is unavailable."
                ),
                expected=expected,
                actual=actual,
            )

        difference = abs(actual - expected)

        if (
            difference
            <= thresholds.duration_tolerance_seconds
        ):
            return RenderQualityCheck(
                check_type=(
                    RenderQualityCheckType.DURATION
                ),
                status=RenderQualityCheckStatus.PASS,
                score=100.0,
                message=(
                    "Output duration matches timeline."
                ),
                expected=expected,
                actual=actual,
                metadata={
                    "difference_seconds": difference,
                },
            )

        return RenderQualityCheck(
            check_type=(
                RenderQualityCheckType.DURATION
            ),
            status=RenderQualityCheckStatus.FAIL,
            score=20.0,
            message=(
                "Output duration differs from timeline."
            ),
            expected=expected,
            actual=actual,
            metadata={
                "difference_seconds": difference,
                "tolerance_seconds": (
                    thresholds
                    .duration_tolerance_seconds
                ),
            },
        )

    def _resolution_check(
        self,
        width: int | None,
        height: int | None,
        thresholds: RenderQualityThresholds,
    ) -> RenderQualityCheck:
        expected = {
            "width": thresholds.expected_width,
            "height": thresholds.expected_height,
        }

        actual = {
            "width": width,
            "height": height,
        }

        if (
            width == thresholds.expected_width
            and height == thresholds.expected_height
        ):
            return RenderQualityCheck(
                check_type=(
                    RenderQualityCheckType.RESOLUTION
                ),
                status=RenderQualityCheckStatus.PASS,
                score=100.0,
                message=(
                    "Output resolution is correct."
                ),
                expected=expected,
                actual=actual,
            )

        return RenderQualityCheck(
            check_type=(
                RenderQualityCheckType.RESOLUTION
            ),
            status=RenderQualityCheckStatus.FAIL,
            score=30.0,
            message=(
                "Output resolution does not match "
                "render configuration."
            ),
            expected=expected,
            actual=actual,
        )

    def _fps_check(
        self,
        actual: float | None,
        thresholds: RenderQualityThresholds,
    ) -> RenderQualityCheck:
        expected = thresholds.expected_fps

        if actual is None or expected is None:
            return RenderQualityCheck(
                check_type=RenderQualityCheckType.FPS,
                status=RenderQualityCheckStatus.WARNING,
                score=70.0,
                message=(
                    "FPS could not be fully verified."
                ),
                expected=expected,
                actual=actual,
            )

        difference = abs(actual - expected)

        if difference <= thresholds.fps_tolerance:
            return RenderQualityCheck(
                check_type=RenderQualityCheckType.FPS,
                status=RenderQualityCheckStatus.PASS,
                score=100.0,
                message="Output FPS is correct.",
                expected=expected,
                actual=actual,
            )

        return RenderQualityCheck(
            check_type=RenderQualityCheckType.FPS,
            status=RenderQualityCheckStatus.WARNING,
            score=60.0,
            message=(
                "Output FPS differs from render "
                "configuration."
            ),
            expected=expected,
            actual=actual,
            metadata={
                "difference": difference,
            },
        )

    def _video_codec_check(
        self,
        codec: str | None,
        thresholds: RenderQualityThresholds,
    ) -> RenderQualityCheck:
        if codec in thresholds.allowed_video_codecs:
            return RenderQualityCheck(
                check_type=(
                    RenderQualityCheckType.VIDEO_CODEC
                ),
                status=RenderQualityCheckStatus.PASS,
                score=100.0,
                message=(
                    "Output video codec is supported."
                ),
                expected=sorted(
                    thresholds.allowed_video_codecs
                ),
                actual=codec,
            )

        return RenderQualityCheck(
            check_type=(
                RenderQualityCheckType.VIDEO_CODEC
            ),
            status=RenderQualityCheckStatus.WARNING,
            score=60.0,
            message=(
                "Output video codec is not in "
                "the preferred codec list."
            ),
            expected=sorted(
                thresholds.allowed_video_codecs
            ),
            actual=codec,
        )

    def _audio_codec_check(
        self,
        codec: str | None,
        has_audio: bool,
        thresholds: RenderQualityThresholds,
    ) -> RenderQualityCheck:
        if not has_audio:
            return RenderQualityCheck(
                check_type=(
                    RenderQualityCheckType.AUDIO_CODEC
                ),
                status=RenderQualityCheckStatus.WARNING,
                score=70.0,
                message=(
                    "Output has no audio stream."
                ),
                actual=None,
            )

        if codec in thresholds.allowed_audio_codecs:
            return RenderQualityCheck(
                check_type=(
                    RenderQualityCheckType.AUDIO_CODEC
                ),
                status=RenderQualityCheckStatus.PASS,
                score=100.0,
                message=(
                    "Output audio codec is supported."
                ),
                expected=sorted(
                    thresholds.allowed_audio_codecs
                ),
                actual=codec,
            )

        return RenderQualityCheck(
            check_type=(
                RenderQualityCheckType.AUDIO_CODEC
            ),
            status=RenderQualityCheckStatus.WARNING,
            score=60.0,
            message=(
                "Output audio codec is not in "
                "the preferred codec list."
            ),
            expected=sorted(
                thresholds.allowed_audio_codecs
            ),
            actual=codec,
        )

    def _black_frame_check(
        self,
        path: Path,
        duration: float,
        thresholds: RenderQualityThresholds,
    ) -> RenderQualityCheck:
        command = [
            self.ffmpeg_binary,
            "-hide_banner",
            "-i",
            str(path),
            "-vf",
            (
                "blackdetect="
                f"d={thresholds.black_frame_min_duration}:"
                f"pic_th={thresholds.black_frame_picture_threshold}:"
                f"pix_th={thresholds.black_frame_pixel_threshold}"
            ),
            "-an",
            "-f",
            "null",
            "-",
        ]

        completed = self._run_detection(command)

        if completed is None:
            return RenderQualityCheck(
                check_type=(
                    RenderQualityCheckType.BLACK_FRAME
                ),
                status=RenderQualityCheckStatus.WARNING,
                score=70.0,
                message=(
                    "Black-frame detection could not run."
                ),
            )

        intervals = self._parse_black_intervals(
            completed.stderr
        )

        total_black = sum(
            interval.duration
            for interval in intervals
        )

        ratio = (
            total_black / duration
            if duration > 0
            else 0.0
        )

        if ratio >= thresholds.max_black_ratio_reject:
            status = RenderQualityCheckStatus.FAIL
            score = 20.0
        elif ratio >= thresholds.max_black_ratio_warning:
            status = RenderQualityCheckStatus.WARNING
            score = 70.0
        else:
            status = RenderQualityCheckStatus.PASS
            score = 100.0

        return RenderQualityCheck(
            check_type=(
                RenderQualityCheckType.BLACK_FRAME
            ),
            status=status,
            score=score,
            message=(
                "Black-frame detection completed."
            ),
            actual={
                "black_duration": total_black,
                "black_ratio": ratio,
            },
            intervals=intervals,
        )

    def _silence_check(
        self,
        path: Path,
        duration: float,
        has_audio: bool,
        thresholds: RenderQualityThresholds,
    ) -> RenderQualityCheck:
        if not has_audio:
            return RenderQualityCheck(
                check_type=(
                    RenderQualityCheckType.SILENCE
                ),
                status=RenderQualityCheckStatus.SKIPPED,
                score=70.0,
                message=(
                    "Silence detection skipped because "
                    "the output has no audio stream."
                ),
            )

        command = [
            self.ffmpeg_binary,
            "-hide_banner",
            "-i",
            str(path),
            "-af",
            (
                "silencedetect="
                f"noise={thresholds.silence_noise_threshold_db}dB:"
                f"d={thresholds.silence_min_duration}"
            ),
            "-vn",
            "-f",
            "null",
            "-",
        ]

        completed = self._run_detection(command)

        if completed is None:
            return RenderQualityCheck(
                check_type=(
                    RenderQualityCheckType.SILENCE
                ),
                status=RenderQualityCheckStatus.WARNING,
                score=70.0,
                message=(
                    "Silence detection could not run."
                ),
            )

        intervals = self._parse_silence_intervals(
            completed.stderr,
            duration,
        )

        total_silence = sum(
            interval.duration
            for interval in intervals
        )

        ratio = (
            total_silence / duration
            if duration > 0
            else 0.0
        )

        if ratio >= thresholds.max_silence_ratio_reject:
            status = RenderQualityCheckStatus.FAIL
            score = 30.0
        elif ratio >= thresholds.max_silence_ratio_warning:
            status = RenderQualityCheckStatus.WARNING
            score = 70.0
        else:
            status = RenderQualityCheckStatus.PASS
            score = 100.0

        return RenderQualityCheck(
            check_type=(
                RenderQualityCheckType.SILENCE
            ),
            status=status,
            score=score,
            message=(
                "Silence detection completed."
            ),
            actual={
                "silence_duration": total_silence,
                "silence_ratio": ratio,
            },
            intervals=intervals,
        )

    def _artifact_integrity_check(
        self,
        context: RenderContext,
        output_path: Path,
    ) -> RenderQualityCheck:
        final_artifact = next(
            (
                item
                for item in context.artifacts
                if item.artifact_id
                == "final_video"
            ),
            None,
        )

        if final_artifact is None:
            return RenderQualityCheck(
                check_type=(
                    RenderQualityCheckType
                    .ARTIFACT_INTEGRITY
                ),
                status=RenderQualityCheckStatus.WARNING,
                score=75.0,
                message=(
                    "Final artifact has not yet been "
                    "attached to RenderContext."
                ),
            )

        artifact_path = Path(
            final_artifact.local_path
        )

        if not artifact_path.exists():
            return RenderQualityCheck(
                check_type=(
                    RenderQualityCheckType
                    .ARTIFACT_INTEGRITY
                ),
                status=RenderQualityCheckStatus.FAIL,
                score=0.0,
                message=(
                    "Final artifact file does not exist."
                ),
                actual=str(artifact_path),
            )

        checksum = self._checksum(artifact_path)

        if (
            final_artifact.checksum
            and checksum
            != final_artifact.checksum
        ):
            return RenderQualityCheck(
                check_type=(
                    RenderQualityCheckType
                    .ARTIFACT_INTEGRITY
                ),
                status=RenderQualityCheckStatus.FAIL,
                score=0.0,
                message=(
                    "Final artifact checksum mismatch."
                ),
                expected=final_artifact.checksum,
                actual=checksum,
            )

        return RenderQualityCheck(
            check_type=(
                RenderQualityCheckType
                .ARTIFACT_INTEGRITY
            ),
            status=RenderQualityCheckStatus.PASS,
            score=100.0,
            message=(
                "Final artifact integrity passed."
            ),
            actual={
                "local_path": str(artifact_path),
                "checksum": checksum,
                "file_size": (
                    artifact_path.stat().st_size
                ),
            },
        )

    def _skipped_media_checks(
        self,
    ) -> list[RenderQualityCheck]:
        values = [
            RenderQualityCheckType.DURATION,
            RenderQualityCheckType.RESOLUTION,
            RenderQualityCheckType.FPS,
            RenderQualityCheckType.VIDEO_CODEC,
            RenderQualityCheckType.AUDIO_CODEC,
            RenderQualityCheckType.BLACK_FRAME,
            RenderQualityCheckType.SILENCE,
        ]

        return [
            RenderQualityCheck(
                check_type=item,
                status=RenderQualityCheckStatus.SKIPPED,
                score=0.0,
                message=(
                    "Check skipped because media "
                    "validation failed."
                ),
            )
            for item in values
        ]

    def _quality_score(
        self,
        checks: list[RenderQualityCheck],
    ) -> float:
        active = [
            check
            for check in checks
            if self._value(check.status)
            != RenderQualityCheckStatus.SKIPPED.value
        ]

        if not active:
            return 0.0

        return round(
            sum(check.score for check in active)
            / len(active),
            2,
        )

    def _run_detection(
        self,
        command: list[str],
    ) -> subprocess.CompletedProcess[str] | None:
        try:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
        except (
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
            return None

        if completed.returncode != 0:
            return None

        return completed

    def _parse_black_intervals(
        self,
        value: str,
    ) -> list[RenderQualityInterval]:
        pattern = re.compile(
            r"black_start:(?P<start>[\d.]+)\s+"
            r"black_end:(?P<end>[\d.]+)\s+"
            r"black_duration:(?P<duration>[\d.]+)"
        )

        return [
            RenderQualityInterval(
                start_time=float(match.group("start")),
                end_time=float(match.group("end")),
                duration=float(
                    match.group("duration")
                ),
            )
            for match in pattern.finditer(value)
        ]

    def _parse_silence_intervals(
        self,
        value: str,
        media_duration: float,
    ) -> list[RenderQualityInterval]:
        starts = [
            float(item)
            for item in re.findall(
                r"silence_start:\s*([\d.]+)",
                value,
            )
        ]

        ends = [
            (
                float(match.group(1)),
                float(match.group(2)),
            )
            for match in re.finditer(
                r"silence_end:\s*([\d.]+)"
                r"\s*\|\s*silence_duration:\s*([\d.]+)",
                value,
            )
        ]

        intervals: list[
            RenderQualityInterval
        ] = []

        for index, start in enumerate(starts):
            if index < len(ends):
                end, duration = ends[index]
            else:
                end = media_duration
                duration = max(
                    0.0,
                    media_duration - start,
                )

            intervals.append(
                RenderQualityInterval(
                    start_time=start,
                    end_time=end,
                    duration=duration,
                )
            )

        return intervals

    def _checksum(
        self,
        path: Path,
    ) -> str:
        digest = hashlib.sha256()

        with path.open("rb") as stream:
            while True:
                chunk = stream.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                digest.update(chunk)

        return digest.hexdigest()

    def _value(self, value) -> str:
        return (
            value.value
            if hasattr(value, "value")
            else str(value)
        )