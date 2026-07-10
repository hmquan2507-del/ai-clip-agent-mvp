from __future__ import annotations

import hashlib
import json
import mimetypes
import shutil
import subprocess
from pathlib import Path

from app.media.validation import MediaValidationRuntime
from app.render.execution.artifact.models import (
    RenderArtifactStoreIssue,
    RenderArtifactStoreResult,
    StoredRenderArtifact,
)
from app.render.execution.context import RenderContext
from app.render.execution.enums import RenderArtifactType
from app.render.execution.models import RenderArtifact
from app.render.ffmpeg.execution import FFmpegExecutionResult


class RenderArtifactStore:
    def __init__(
        self,
        media_validator: MediaValidationRuntime | None = None,
        ffmpeg_binary: str = "ffmpeg",
        checksum_chunk_size: int = 1024 * 1024,
    ):
        self.media_validator = (
            media_validator or MediaValidationRuntime()
        )
        self.ffmpeg_binary = ffmpeg_binary
        self.checksum_chunk_size = checksum_chunk_size

    def store(
        self,
        context: RenderContext,
        execution_result: FFmpegExecutionResult,
        generate_thumbnail: bool = True,
        generate_report: bool = True,
    ) -> RenderArtifactStoreResult:
        context.ensure_directories()

        artifact_root = Path(
            context.artifact_directory
        )
        artifact_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        artifacts: list[StoredRenderArtifact] = []
        issues: list[RenderArtifactStoreIssue] = []

        if not execution_result.success:
            issues.append(
                RenderArtifactStoreIssue(
                    level="error",
                    code="ffmpeg_execution_failed",
                    message=(
                        "Cannot store final video because "
                        "FFmpeg execution was not successful."
                    ),
                    metadata={
                        "returncode": execution_result.returncode,
                        "error_count": len(
                            execution_result.issues
                        ),
                    },
                )
            )

        final_video = self._store_final_video(
            context=context,
            execution_result=execution_result,
            artifact_root=artifact_root,
            issues=issues,
        )

        if final_video is not None:
            artifacts.append(final_video)

        if (
            generate_thumbnail
            and final_video is not None
        ):
            thumbnail = self._generate_thumbnail(
                final_video_path=Path(
                    final_video.local_path
                ),
                artifact_root=artifact_root,
                issues=issues,
            )

            if thumbnail is not None:
                artifacts.append(thumbnail)

        if generate_report:
            report = self._write_render_report(
                execution_result=execution_result,
                artifact_root=artifact_root,
                issues=issues,
            )

            if report is not None:
                artifacts.append(report)

        manifest_path = (
            artifact_root / "render_artifacts_manifest.json"
        )

        success = (
            final_video is not None
            and not any(
                issue.level == "error"
                for issue in issues
            )
        )

        result = RenderArtifactStoreResult(
            production_id=context.production_id,
            success=success,
            artifacts=artifacts,
            issues=issues,
            manifest_path=str(manifest_path),
            metadata={
                "runtime": "RenderArtifactStore",
                "artifact_count": len(artifacts),
                "issue_count": len(issues),
                "generate_thumbnail": generate_thumbnail,
                "generate_report": generate_report,
            },
        )

        manifest_path.write_text(
            json.dumps(
                result.to_dict(),
                ensure_ascii=False,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )

        self._attach_to_context(
            context=context,
            artifacts=artifacts,
            manifest_path=str(manifest_path),
        )

        return result

    def _store_final_video(
        self,
        context: RenderContext,
        execution_result: FFmpegExecutionResult,
        artifact_root: Path,
        issues: list[RenderArtifactStoreIssue],
    ) -> StoredRenderArtifact | None:
        source_path = Path(
            execution_result.output_path
        )

        if not source_path.exists():
            issues.append(
                RenderArtifactStoreIssue(
                    level="error",
                    code="final_video_missing",
                    message=(
                        "Rendered final video does not exist."
                    ),
                    artifact_id="final_video",
                    metadata={
                        "source_path": str(source_path),
                    },
                )
            )
            return None

        validation = self.media_validator.validate(
            local_path=str(source_path),
            require_video=True,
        )

        if not validation.valid:
            issues.append(
                RenderArtifactStoreIssue(
                    level="error",
                    code="final_video_invalid",
                    message=(
                        "Rendered final video failed validation."
                    ),
                    artifact_id="final_video",
                    metadata=validation.to_dict(),
                )
            )
            return None

        target_path = (
            artifact_root / "final.mp4"
        )

        if source_path.resolve() != target_path.resolve():
            shutil.copy2(
                source_path,
                target_path,
            )
        else:
            target_path = source_path

        return StoredRenderArtifact(
            artifact_id="final_video",
            artifact_type=(
                RenderArtifactType.FINAL_VIDEO.value
            ),
            local_path=str(target_path),
            mime_type="video/mp4",
            checksum=self._checksum(target_path),
            file_size=target_path.stat().st_size,
            duration=validation.duration,
            width=validation.width,
            height=validation.height,
            fps=validation.fps,
            video_codec=validation.video_codec,
            audio_codec=validation.audio_codec,
            metadata={
                "source_output_path": (
                    execution_result.output_path
                ),
                "ffmpeg_returncode": (
                    execution_result.returncode
                ),
            },
        )

    def _generate_thumbnail(
        self,
        final_video_path: Path,
        artifact_root: Path,
        issues: list[RenderArtifactStoreIssue],
    ) -> StoredRenderArtifact | None:
        thumbnail_path = (
            artifact_root / "thumbnail.jpg"
        )

        command = [
            self.ffmpeg_binary,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            "1",
            "-i",
            str(final_video_path),
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(thumbnail_path),
        ]

        try:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=120,
            )

        except FileNotFoundError:
            issues.append(
                RenderArtifactStoreIssue(
                    level="error",
                    code="ffmpeg_not_installed",
                    message=(
                        "FFmpeg executable was not found "
                        "while generating thumbnail."
                    ),
                    artifact_id="thumbnail",
                )
            )
            return None

        except subprocess.TimeoutExpired:
            issues.append(
                RenderArtifactStoreIssue(
                    level="error",
                    code="thumbnail_timeout",
                    message=(
                        "Thumbnail generation timed out."
                    ),
                    artifact_id="thumbnail",
                )
            )
            return None

        if completed.returncode != 0:
            issues.append(
                RenderArtifactStoreIssue(
                    level="error",
                    code="thumbnail_generation_failed",
                    message=(
                        completed.stderr.strip()
                        or "Thumbnail generation failed."
                    ),
                    artifact_id="thumbnail",
                    metadata={
                        "returncode": completed.returncode,
                    },
                )
            )
            return None

        if (
            not thumbnail_path.exists()
            or thumbnail_path.stat().st_size <= 0
        ):
            issues.append(
                RenderArtifactStoreIssue(
                    level="error",
                    code="thumbnail_missing",
                    message=(
                        "Thumbnail output was not created."
                    ),
                    artifact_id="thumbnail",
                )
            )
            return None

        return StoredRenderArtifact(
            artifact_id="thumbnail",
            artifact_type=(
                RenderArtifactType.THUMBNAIL.value
            ),
            local_path=str(thumbnail_path),
            mime_type="image/jpeg",
            checksum=self._checksum(
                thumbnail_path
            ),
            file_size=(
                thumbnail_path.stat().st_size
            ),
            metadata={
                "source_video": str(
                    final_video_path
                ),
                "capture_time": 1.0,
            },
        )

    def _write_render_report(
        self,
        execution_result: FFmpegExecutionResult,
        artifact_root: Path,
        issues: list[RenderArtifactStoreIssue],
    ) -> StoredRenderArtifact | None:
        report_path = (
            artifact_root / "render_report.json"
        )

        try:
            report_path.write_text(
                json.dumps(
                    execution_result.to_dict(),
                    ensure_ascii=False,
                    indent=2,
                    default=str,
                ),
                encoding="utf-8",
            )

        except OSError as error:
            issues.append(
                RenderArtifactStoreIssue(
                    level="error",
                    code="render_report_write_failed",
                    message=str(error),
                    artifact_id="render_report",
                )
            )
            return None

        return StoredRenderArtifact(
            artifact_id="render_report",
            artifact_type=(
                RenderArtifactType.RENDER_REPORT.value
            ),
            local_path=str(report_path),
            mime_type="application/json",
            checksum=self._checksum(
                report_path
            ),
            file_size=report_path.stat().st_size,
            metadata={
                "success": execution_result.success,
                "returncode": execution_result.returncode,
            },
        )

    def _attach_to_context(
        self,
        context: RenderContext,
        artifacts: list[StoredRenderArtifact],
        manifest_path: str,
    ) -> None:
        context.artifacts = [
            RenderArtifact(
                artifact_id=item.artifact_id,
                artifact_type=item.artifact_type,
                local_path=item.local_path,
                mime_type=item.mime_type,
                checksum=item.checksum,
                size=item.file_size,
                metadata={
                    **item.metadata,
                    "duration": item.duration,
                    "width": item.width,
                    "height": item.height,
                    "fps": item.fps,
                    "video_codec": item.video_codec,
                    "audio_codec": item.audio_codec,
                },
            )
            for item in artifacts
        ]

        context.metadata = {
            **context.metadata,
            "render_artifact_manifest": (
                manifest_path
            ),
            "render_artifact_count": len(
                context.artifacts
            ),
        }

    def _checksum(
        self,
        path: Path,
    ) -> str:
        digest = hashlib.sha256()

        with path.open("rb") as stream:
            while True:
                chunk = stream.read(
                    self.checksum_chunk_size
                )

                if not chunk:
                    break

                digest.update(chunk)

        return digest.hexdigest()