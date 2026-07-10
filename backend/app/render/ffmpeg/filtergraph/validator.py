from __future__ import annotations

import subprocess
from pathlib import Path

from app.render.ffmpeg.filtergraph.models import (
    FFmpegFilterGraph,
    FFmpegFilterGraphIssue,
)


class FFmpegFilterGraphValidator:
    def __init__(
        self,
        ffmpeg_binary: str = "ffmpeg",
        timeout_seconds: int = 120,
    ):
        self.ffmpeg_binary = ffmpeg_binary
        self.timeout_seconds = timeout_seconds

    def validate_contract(
        self,
        graph: FFmpegFilterGraph,
    ) -> FFmpegFilterGraph:
        issues = list(graph.issues)

        if not graph.input_arguments:
            issues.append(
                FFmpegFilterGraphIssue(
                    level="error",
                    code="missing_inputs",
                    message=(
                        "FFmpeg filter graph has no inputs."
                    ),
                )
            )

        if not graph.video_output_label:
            issues.append(
                FFmpegFilterGraphIssue(
                    level="error",
                    code="missing_video_output",
                    message=(
                        "FFmpeg filter graph has no "
                        "video output label."
                    ),
                )
            )

        output_labels: set[str] = set()

        for chain in graph.chains:
            if (
                chain.output_label
                and chain.output_label
                in output_labels
            ):
                issues.append(
                    FFmpegFilterGraphIssue(
                        level="error",
                        code="duplicate_output_label",
                        message=(
                            "FFmpeg filter output labels "
                            "must be unique."
                        ),
                        chain_id=chain.chain_id,
                        metadata={
                            "output_label": (
                                chain.output_label
                            ),
                        },
                    )
                )

            if chain.output_label:
                output_labels.add(
                    chain.output_label
                )

            if not chain.filter_text.strip():
                issues.append(
                    FFmpegFilterGraphIssue(
                        level="error",
                        code="empty_filter_chain",
                        message=(
                            "FFmpeg filter chain is empty."
                        ),
                        chain_id=chain.chain_id,
                    )
                )

        graph.issues = issues

        graph.metadata = {
            **graph.metadata,
            "contract_valid": not any(
                issue.level == "error"
                for issue in issues
            ),
            "issue_count": len(issues),
        }

        return graph

    def validate_with_ffmpeg(
        self,
        graph: FFmpegFilterGraph,
        validation_duration: float = 1.0,
    ) -> FFmpegFilterGraph:
        graph = self.validate_contract(graph)

        if not graph.metadata.get(
            "contract_valid",
            False,
        ):
            return graph

        command = [self.ffmpeg_binary, "-y"]

        for item in sorted(
            graph.input_arguments,
            key=lambda value: value.input_index,
        ):
            if not Path(
                item.prepared_path
            ).exists():
                graph.issues.append(
                    FFmpegFilterGraphIssue(
                        level="error",
                        code="prepared_input_missing",
                        message=(
                            "Prepared FFmpeg input "
                            "does not exist."
                        ),
                        metadata={
                            "input_id": item.input_id,
                            "prepared_path": (
                                item.prepared_path
                            ),
                        },
                    )
                )
                continue

            command.extend(item.arguments)

        if any(
            issue.level == "error"
            for issue in graph.issues
        ):
            graph.metadata["ffmpeg_valid"] = False
            graph.metadata["issue_count"] = len(
                graph.issues
            )
            return graph

        command.extend(
            [
                "-filter_complex",
                graph.filter_complex,
            ]
        )

        command.extend(graph.map_arguments)

        command.extend(
            [
                "-t",
                str(validation_duration),
                "-f",
                "null",
                "-",
            ]
        )

        try:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )

        except FileNotFoundError:
            graph.issues.append(
                FFmpegFilterGraphIssue(
                    level="error",
                    code="ffmpeg_not_installed",
                    message=(
                        "FFmpeg executable was not found."
                    ),
                )
            )

            graph.metadata["ffmpeg_valid"] = False
            graph.metadata["issue_count"] = len(
                graph.issues
            )

            return graph

        except subprocess.TimeoutExpired:
            graph.issues.append(
                FFmpegFilterGraphIssue(
                    level="error",
                    code="ffmpeg_validation_timeout",
                    message=(
                        "FFmpeg filter graph validation "
                        "timed out."
                    ),
                )
            )

            graph.metadata["ffmpeg_valid"] = False
            graph.metadata["issue_count"] = len(
                graph.issues
            )

            return graph

        if completed.returncode != 0:
            graph.issues.append(
                FFmpegFilterGraphIssue(
                    level="error",
                    code="ffmpeg_filtergraph_invalid",
                    message=(
                        completed.stderr.strip()
                        or "FFmpeg filter graph validation failed."
                    ),
                    metadata={
                        "returncode": (
                            completed.returncode
                        ),
                        "command": command,
                    },
                )
            )

        graph.metadata = {
            **graph.metadata,
            "ffmpeg_valid": (
                completed.returncode == 0
            ),
            "ffmpeg_returncode": (
                completed.returncode
            ),
            "issue_count": len(graph.issues),
        }

        return graph