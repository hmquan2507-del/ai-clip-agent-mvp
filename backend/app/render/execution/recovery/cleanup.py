from __future__ import annotations

import shutil
from pathlib import Path

from app.render.execution.context import RenderContext
from app.render.execution.recovery.enums import (
    RenderCleanupMode,
)
from app.render.execution.recovery.models import (
    RenderCleanupResult,
)


class RenderCleanupRuntime:
    def cleanup(
        self,
        context: RenderContext,
        mode: RenderCleanupMode | str,
        preserve_diagnostics: bool = True,
    ) -> RenderCleanupResult:
        mode_value = (
            mode.value
            if hasattr(mode, "value")
            else str(mode)
        )

        removed_paths: list[str] = []
        preserved_paths: list[str] = []
        issues: list[str] = []

        if mode_value == RenderCleanupMode.NONE.value:
            return RenderCleanupResult(
                success=True,
                removed_paths=[],
                preserved_paths=[],
                issues=[],
                metadata={
                    "cleanup_mode": mode_value,
                },
            )

        candidates: list[Path] = []

        output_directory = Path(
            context.output_directory
        )
        temp_directory = Path(
            context.temp_directory
        )

        final_output = (
            output_directory / "final.mp4"
        )

        if final_output.exists():
            candidates.append(final_output)

        for partial_path in (
            output_directory.glob("*.part")
            if output_directory.exists()
            else []
        ):
            candidates.append(partial_path)

        if mode_value == RenderCleanupMode.FULL.value:
            if temp_directory.exists():
                candidates.append(temp_directory)

            working_temp = (
                Path(context.working_directory)
                / "ffmpeg_temp"
            )

            if working_temp.exists():
                candidates.append(working_temp)

        unique_candidates: list[Path] = []

        seen: set[str] = set()

        for candidate in candidates:
            resolved = str(candidate)

            if resolved in seen:
                continue

            seen.add(resolved)
            unique_candidates.append(candidate)

        for candidate in unique_candidates:
            try:
                if (
                    preserve_diagnostics
                    and self._is_diagnostic(candidate)
                ):
                    preserved_paths.append(
                        str(candidate)
                    )
                    continue

                if candidate.is_dir():
                    shutil.rmtree(candidate)
                elif candidate.exists():
                    candidate.unlink()

                removed_paths.append(
                    str(candidate)
                )

            except OSError as error:
                issues.append(
                    f"{candidate}: {error}"
                )

        return RenderCleanupResult(
            success=not issues,
            removed_paths=removed_paths,
            preserved_paths=preserved_paths,
            issues=issues,
            metadata={
                "cleanup_mode": mode_value,
                "preserve_diagnostics": (
                    preserve_diagnostics
                ),
            },
        )

    def cleanup_after_success(
        self,
        context: RenderContext,
        remove_temp: bool = True,
        remove_working_prepared_inputs: bool = False,
    ) -> RenderCleanupResult:
        removed_paths: list[str] = []
        preserved_paths: list[str] = []
        issues: list[str] = []

        candidates: list[Path] = []

        if remove_temp:
            candidates.append(
                Path(context.temp_directory)
            )

        if remove_working_prepared_inputs:
            candidates.append(
                Path(context.working_directory)
                / "prepared_inputs"
            )

        for candidate in candidates:
            try:
                if not candidate.exists():
                    continue

                shutil.rmtree(candidate)

                removed_paths.append(
                    str(candidate)
                )

            except OSError as error:
                issues.append(
                    f"{candidate}: {error}"
                )

        artifact_directory = Path(
            context.artifact_directory
        )

        if artifact_directory.exists():
            preserved_paths.append(
                str(artifact_directory)
            )

        return RenderCleanupResult(
            success=not issues,
            removed_paths=removed_paths,
            preserved_paths=preserved_paths,
            issues=issues,
            metadata={
                "cleanup_after_success": True,
                "remove_temp": remove_temp,
                "remove_working_prepared_inputs": (
                    remove_working_prepared_inputs
                ),
            },
        )

    def _is_diagnostic(
        self,
        path: Path,
    ) -> bool:
        diagnostic_names = {
            "render_report.json",
            "render_artifacts_manifest.json",
            "prepared_inputs_manifest.json",
            "recovery_diagnostics.json",
        }

        return path.name in diagnostic_names