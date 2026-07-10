from __future__ import annotations

from app.render.ffmpeg.instructions.compiler import (
    FFmpegInstructionCompiler,
)
from app.render.ffmpeg.instructions.validator import (
    FFmpegInstructionPlanValidator,
)


def build_ffmpeg_instruction_compiler() -> (
    FFmpegInstructionCompiler
):
    return FFmpegInstructionCompiler()


def build_ffmpeg_instruction_plan_validator() -> (
    FFmpegInstructionPlanValidator
):
    return FFmpegInstructionPlanValidator()