from __future__ import annotations

from typing import Any

from app.render.ffmpeg.ffmpeg_command_builder import FFmpegCommandBuilder
from app.render.ffmpeg.models import FFmpegCommandPlan


class FFmpegRuntime:
    runtime_name = "ffmpeg_runtime"

    def __init__(self):
        self.command_builder = FFmpegCommandBuilder()

    def build_command_plan(
        self,
        production_id: str,
        render_schedule: dict[str, Any],
        resolved_assets: dict[str, Any],
    ) -> FFmpegCommandPlan:
        return self.command_builder.build(
            production_id=production_id,
            render_schedule=render_schedule,
            resolved_assets=resolved_assets,
        )