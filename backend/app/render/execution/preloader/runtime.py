from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path

from app.media.validation import MediaValidationRuntime
from app.render.execution.context import RenderContext
from app.render.execution.preloader.models import (
    PreparedRenderInput,
    RenderAssetPreloadIssue,
    RenderAssetPreloadResult,
)
from app.timeline.compiler.models import TimelineInput


class RenderAssetPreloader:
    def __init__(
        self,
        media_validator: MediaValidationRuntime | None = None,
        prefer_hardlink: bool = True,
        checksum_chunk_size: int = 1024 * 1024,
    ):
        self.media_validator = (
            media_validator or MediaValidationRuntime()
        )
        self.prefer_hardlink = prefer_hardlink
        self.checksum_chunk_size = checksum_chunk_size

    def preload(
        self,
        context: RenderContext,
    ) -> RenderAssetPreloadResult:
        context.ensure_directories()

        prepared_root = (
            Path(context.working_directory)
            / "prepared_inputs"
        )
        prepared_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        prepared_inputs: list[PreparedRenderInput] = []
        issues: list[RenderAssetPreloadIssue] = []

        for timeline_input in (
            context.execution_timeline.inputs
        ):
            try:
                prepared = self._prepare_input(
                    timeline_input=timeline_input,
                    prepared_root=prepared_root,
                )
                prepared_inputs.append(prepared)

            except Exception as error:
                issues.append(
                    RenderAssetPreloadIssue(
                        level="error",
                        code="input_preload_failed",
                        message=str(error),
                        input_id=timeline_input.input_id,
                        metadata={
                            "local_path": (
                                timeline_input.local_path
                            ),
                            "input_type": (
                                timeline_input.input_type
                            ),
                        },
                    )
                )

        manifest_path = (
            Path(context.artifact_directory)
            / "prepared_inputs_manifest.json"
        )

        success = not any(
            issue.level == "error"
            for issue in issues
        )

        result = RenderAssetPreloadResult(
            production_id=context.production_id,
            prepared_inputs=prepared_inputs,
            issues=issues,
            manifest_path=str(manifest_path),
            success=success,
            metadata={
                "runtime": "RenderAssetPreloader",
                "input_count": len(
                    context.execution_timeline.inputs
                ),
                "prepared_input_count": len(
                    prepared_inputs
                ),
                "issue_count": len(issues),
                "prefer_hardlink": (
                    self.prefer_hardlink
                ),
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

        context.metadata = {
            **context.metadata,
            "prepared_inputs_manifest": (
                str(manifest_path)
            ),
            "prepared_input_count": len(
                prepared_inputs
            ),
            "asset_preload_success": success,
        }

        context.runtime_state.metadata = {
            **context.runtime_state.metadata,
            "prepared_inputs": {
                item.input_id: item.to_dict()
                for item in prepared_inputs
            },
        }

        return result

    def _prepare_input(
        self,
        timeline_input: TimelineInput,
        prepared_root: Path,
    ) -> PreparedRenderInput:
        source_path = Path(
            timeline_input.local_path
        ).expanduser()

        if not source_path.exists():
            raise FileNotFoundError(
                f"Render input does not exist: "
                f"{source_path}"
            )

        if not source_path.is_file():
            raise ValueError(
                f"Render input is not a file: "
                f"{source_path}"
            )

        validation = self.media_validator.validate(
            local_path=str(source_path),
            require_video=(
                timeline_input.input_type == "video"
            ),
        )

        if not validation.valid:
            raise RuntimeError(
                "Render input failed media validation: "
                f"{timeline_input.input_id}, "
                f"errors={validation.errors}"
            )

        extension = self._resolve_extension(
            source_path=source_path,
            input_type=timeline_input.input_type,
        )

        target_name = (
            f"{timeline_input.input_id}{extension}"
        )

        prepared_path = (
            prepared_root / target_name
        )

        source_checksum = self._checksum(
            source_path
        )

        reused = False
        copied = False
        linked = False

        if prepared_path.exists():
            prepared_checksum = self._checksum(
                prepared_path
            )

            if prepared_checksum == source_checksum:
                reused = True
            else:
                prepared_path.unlink()

        if not reused:
            linked = self._try_hardlink(
                source_path=source_path,
                prepared_path=prepared_path,
            )

            if not linked:
                shutil.copy2(
                    source_path,
                    prepared_path,
                )
                copied = True

        file_size = prepared_path.stat().st_size

        return PreparedRenderInput(
            input_id=timeline_input.input_id,
            input_type=timeline_input.input_type,
            source_path=str(source_path),
            prepared_path=str(prepared_path),
            asset_id=timeline_input.asset_id,
            checksum=source_checksum,
            file_size=file_size,
            duration=validation.duration,
            width=validation.width,
            height=validation.height,
            fps=validation.fps,
            video_codec=validation.video_codec,
            audio_codec=validation.audio_codec,
            has_video=validation.has_video,
            has_audio=validation.has_audio,
            copied=copied,
            linked=linked,
            reused=reused,
            metadata={
                **timeline_input.metadata,
                "validation": (
                    validation.to_dict()
                ),
            },
        )

    def _try_hardlink(
        self,
        source_path: Path,
        prepared_path: Path,
    ) -> bool:
        if not self.prefer_hardlink:
            return False

        try:
            os.link(
                source_path,
                prepared_path,
            )
            return True
        except (
            OSError,
            PermissionError,
            FileExistsError,
        ):
            return False

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

    def _resolve_extension(
        self,
        source_path: Path,
        input_type: str,
    ) -> str:
        suffix = source_path.suffix.lower()

        if suffix:
            return suffix

        if input_type == "video":
            return ".mp4"

        if input_type == "audio":
            return ".mp3"

        return ".bin"