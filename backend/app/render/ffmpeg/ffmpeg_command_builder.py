from __future__ import annotations

from typing import Any

from app.render.ffmpeg.ffmpeg_filter_builder import FFmpegFilterBuilder
from app.render.ffmpeg.models import FFmpegCommand, FFmpegCommandPlan


class FFmpegCommandBuilder:
    def __init__(self):
        self.filter_builder = FFmpegFilterBuilder()

    def build(
        self,
        production_id: str,
        render_schedule: dict[str, Any],
        resolved_assets: dict[str, Any],
    ) -> FFmpegCommandPlan:
        source_video = self._source_video_path(resolved_assets)
        output_path = self._output_path(
            production_id=production_id,
            resolved_assets=resolved_assets,
        )

        filter_groups = self.filter_builder.build_filters(
            render_schedule=render_schedule,
            resolved_assets=resolved_assets,
        )

        video_filters = filter_groups.get("video", [])
        audio_filters = filter_groups.get("audio", [])

        args = [
            "ffmpeg",
            "-y",
            "-i",
            source_video,
        ]

        if video_filters:
            args.extend(
                [
                    "-vf",
                    ",".join(video_filters),
                ]
            )

        if audio_filters:
            args.extend(
                [
                    "-af",
                    ",".join(audio_filters),
                ]
            )

        args.extend(
            [
                "-c:v",
                "libx264",
                "-c:a",
                "aac",
                output_path,
            ]
        )

        warnings = self._warnings(
            resolved_assets=resolved_assets,
            source_video=source_video,
            video_filters=video_filters,
            audio_filters=audio_filters,
        )

        command = FFmpegCommand(
            command_id="ffmpeg_command_0",
            args=args,
            command_preview=" ".join(args),
            metadata={
                "source_video": source_video,
                "output_path": output_path,
                "video_filter_count": len(video_filters),
                "audio_filter_count": len(audio_filters),
                "is_placeholder_safe": self._is_placeholder_source(
                    resolved_assets
                ),
                "warnings": warnings,
            },
        )

        return FFmpegCommandPlan(
            production_id=production_id,
            commands=[command],
            metadata={
                "builder": "ffmpeg_command_builder",
                "command_count": 1,
                "mode": "command_plan_only",
                "executes_ffmpeg": False,
                "warnings": warnings,
            },
        )

    def _source_video_path(
        self,
        resolved_assets: dict[str, Any],
    ) -> str:
        assets = resolved_assets.get("assets", [])

        if isinstance(assets, list):
            for asset in assets:
                if not isinstance(asset, dict):
                    continue

                if asset.get("asset_type") != "source_video":
                    continue

                local_path = asset.get("local_path")
                if local_path:
                    return str(local_path)

        return "storage/placeholders/source_video.mp4"

    def _output_path(
        self,
        production_id: str,
        resolved_assets: dict[str, Any],
    ) -> str:
        output_path = resolved_assets.get("output_path")

        if output_path:
            return str(output_path)

        return f"storage/renders/{production_id}/final.mp4"

    def _is_placeholder_source(
        self,
        resolved_assets: dict[str, Any],
    ) -> bool:
        assets = resolved_assets.get("assets", [])

        if not isinstance(assets, list):
            return True

        for asset in assets:
            if not isinstance(asset, dict):
                continue

            if asset.get("asset_type") == "source_video":
                return bool(asset.get("is_placeholder"))

        return True

    def _warnings(
        self,
        resolved_assets: dict[str, Any],
        source_video: str,
        video_filters: list[str],
        audio_filters: list[str],
    ) -> list[str]:
        warnings: list[str] = []

        if self._is_placeholder_source(resolved_assets):
            warnings.append("source_video_is_placeholder")

        if source_video == "storage/placeholders/source_video.mp4":
            warnings.append("using_default_placeholder_source_video")

        if not video_filters:
            warnings.append("no_video_filters_generated")

        if not audio_filters:
            warnings.append("no_audio_filters_generated")

        return warnings