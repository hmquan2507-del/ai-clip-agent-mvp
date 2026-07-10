from __future__ import annotations

from app.render.ffmpeg.filtergraph.builder import (
    FFmpegFilterGraphBuilder,
)
from app.render.ffmpeg.filtergraph.validator import (
    FFmpegFilterGraphValidator,
)


def build_ffmpeg_filtergraph_builder() -> (
    FFmpegFilterGraphBuilder
):
    return FFmpegFilterGraphBuilder()


def build_ffmpeg_filtergraph_validator() -> (
    FFmpegFilterGraphValidator
):
    return FFmpegFilterGraphValidator()