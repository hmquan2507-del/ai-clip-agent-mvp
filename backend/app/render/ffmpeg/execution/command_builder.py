from __future__ import annotations

from pathlib import Path

from app.render.ffmpeg.execution.models import FFmpegCommand
from app.render.ffmpeg.filtergraph.models import FFmpegFilterGraph


class FFmpegCommandBuilder:
    def __init__(
        self,
        ffmpeg_binary: str = "ffmpeg",
    ):
        self.ffmpeg_binary = ffmpeg_binary

    def build(
        self,
        graph: FFmpegFilterGraph,
        enable_progress: bool = True,
        log_level: str = "error",
    ) -> FFmpegCommand:
        output_path = Path(graph.output_path)
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        arguments: list[str] = [
            "-y",
            "-hide_banner",
            "-loglevel",
            log_level,
        ]

        if enable_progress:
            arguments.extend(
                [
                    "-progress",
                    "pipe:1",
                    "-nostats",
                ]
            )

        for item in sorted(
            graph.input_arguments,
            key=lambda value: value.input_index,
        ):
            arguments.extend(item.arguments)

        if graph.filter_complex:
            arguments.extend(
                [
                    "-filter_complex",
                    graph.filter_complex,
                ]
            )

        arguments.extend(graph.map_arguments)
        arguments.extend(graph.output_arguments)
        arguments.append(str(output_path))

        return FFmpegCommand(
            binary=self.ffmpeg_binary,
            arguments=arguments,
            output_path=str(output_path),
            duration=self._resolve_duration(graph),
            metadata={
                "builder": "FFmpegCommandBuilder",
                "filtergraph_version": graph.version,
                "input_count": len(graph.input_arguments),
                "chain_count": len(graph.chains),
                "progress_enabled": enable_progress,
                "log_level": log_level,
            },
        )

    def _resolve_duration(
        self,
        graph: FFmpegFilterGraph,
    ) -> float:
        duration = graph.metadata.get(
            "duration"
        )

        if isinstance(duration, (int, float)):
            return max(0.0, float(duration))

        for index, argument in enumerate(
            graph.output_arguments
        ):
            if argument != "-t":
                continue

            if index + 1 >= len(
                graph.output_arguments
            ):
                continue

            try:
                return max(
                    0.0,
                    float(
                        graph.output_arguments[
                            index + 1
                        ]
                    ),
                )
            except (TypeError, ValueError):
                continue

        return 0.0