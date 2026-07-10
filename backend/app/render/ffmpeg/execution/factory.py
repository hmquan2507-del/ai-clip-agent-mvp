from __future__ import annotations

from app.render.ffmpeg.execution.command_builder import (
    FFmpegCommandBuilder,
)
from app.render.ffmpeg.execution.executor import (
    FFmpegCommandExecutor,
)


def build_ffmpeg_command_builder() -> (
    FFmpegCommandBuilder
):
    return FFmpegCommandBuilder()


def build_ffmpeg_command_executor() -> (
    FFmpegCommandExecutor
):
    return FFmpegCommandExecutor()