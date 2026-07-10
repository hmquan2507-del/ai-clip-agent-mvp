from __future__ import annotations

from app.render.execution.context import RenderContext
from app.render.execution.enums import (
    RenderNodeStatus,
    RenderNodeType,
    RenderStage,
)
from app.render.execution.interfaces import (
    BaseRenderGraphBuilder,
)
from app.render.execution.models import (
    RenderGraph,
    RenderNode,
)


class RenderGraphBuilder(BaseRenderGraphBuilder):
    def build(
        self,
        context: RenderContext,
    ) -> RenderGraph:
        timeline = context.execution_timeline
        nodes: list[RenderNode] = []

        nodes.append(
            RenderNode(
                node_id="prepare_inputs",
                node_type=RenderNodeType.PREPARE_INPUTS,
                stage=RenderStage.PREPARE,
                dependencies=[],
                status=RenderNodeStatus.PENDING,
                inputs={
                    "timeline_inputs": [
                        item.to_dict()
                        for item in timeline.inputs
                    ],
                },
                priority=10,
            )
        )

        nodes.append(
            RenderNode(
                node_id="decode_video",
                node_type=RenderNodeType.DECODE_VIDEO,
                stage=RenderStage.DECODE,
                dependencies=["prepare_inputs"],
                inputs=self._instructions_by_type(
                    context,
                    {
                        "place_video",
                        "place_video_overlay",
                    },
                ),
                priority=20,
            )
        )

        if self._has_instruction(
            context,
            {"place_audio"},
        ):
            nodes.append(
                RenderNode(
                    node_id="decode_audio",
                    node_type=RenderNodeType.DECODE_AUDIO,
                    stage=RenderStage.DECODE,
                    dependencies=["prepare_inputs"],
                    inputs=self._instructions_by_type(
                        context,
                        {"place_audio"},
                    ),
                    priority=20,
                )
            )

        nodes.append(
            RenderNode(
                node_id="compose_primary_video",
                node_type=(
                    RenderNodeType.COMPOSE_PRIMARY_VIDEO
                ),
                stage=RenderStage.VIDEO,
                dependencies=["decode_video"],
                inputs=self._instructions_by_type(
                    context,
                    {"place_video"},
                ),
                priority=30,
            )
        )

        last_video_node = "compose_primary_video"

        if self._has_instruction(
            context,
            {"place_video_overlay"},
        ):
            nodes.append(
                RenderNode(
                    node_id="overlay_broll",
                    node_type=RenderNodeType.OVERLAY_BROLL,
                    stage=RenderStage.VIDEO,
                    dependencies=[last_video_node],
                    inputs=self._instructions_by_type(
                        context,
                        {"place_video_overlay"},
                    ),
                    priority=40,
                )
            )

            last_video_node = "overlay_broll"

        if self._has_instruction(
            context,
            {"apply_effect"},
        ):
            nodes.append(
                RenderNode(
                    node_id="apply_effects",
                    node_type=RenderNodeType.APPLY_EFFECTS,
                    stage=RenderStage.EFFECT,
                    dependencies=[last_video_node],
                    inputs=self._instructions_by_type(
                        context,
                        {"apply_effect"},
                    ),
                    priority=50,
                )
            )

            last_video_node = "apply_effects"

        if self._has_instruction(
            context,
            {"apply_transition"},
        ):
            nodes.append(
                RenderNode(
                    node_id="apply_transitions",
                    node_type=RenderNodeType.APPLY_TRANSITIONS,
                    stage=RenderStage.EFFECT,
                    dependencies=[last_video_node],
                    inputs=self._instructions_by_type(
                        context,
                        {"apply_transition"},
                    ),
                    priority=60,
                )
            )

            last_video_node = "apply_transitions"

        if self._has_instruction(
            context,
            {"draw_subtitle"},
        ):
            nodes.append(
                RenderNode(
                    node_id="draw_subtitles",
                    node_type=RenderNodeType.DRAW_SUBTITLES,
                    stage=RenderStage.SUBTITLE,
                    dependencies=[last_video_node],
                    inputs=self._instructions_by_type(
                        context,
                        {"draw_subtitle"},
                    ),
                    priority=70,
                )
            )

            last_video_node = "draw_subtitles"

        audio_dependency: list[str] = []

        if any(
            node.node_id == "decode_audio"
            for node in nodes
        ):
            nodes.append(
                RenderNode(
                    node_id="mix_audio",
                    node_type=RenderNodeType.MIX_AUDIO,
                    stage=RenderStage.AUDIO,
                    dependencies=["decode_audio"],
                    inputs=self._instructions_by_type(
                        context,
                        {"place_audio"},
                    ),
                    priority=70,
                )
            )

            audio_dependency = ["mix_audio"]

        encode_dependencies = [
            last_video_node,
            *audio_dependency,
        ]

        nodes.append(
            RenderNode(
                node_id="encode_video",
                node_type=RenderNodeType.ENCODE_VIDEO,
                stage=RenderStage.ENCODE,
                dependencies=encode_dependencies,
                inputs={
                    "canvas": {
                        "width": timeline.width,
                        "height": timeline.height,
                        "fps": timeline.fps,
                    },
                    "duration": timeline.duration,
                    "render_config": (
                        context.render_config.to_dict()
                    ),
                },
                priority=90,
            )
        )

        nodes.append(
            RenderNode(
                node_id="write_artifacts",
                node_type=RenderNodeType.WRITE_ARTIFACTS,
                stage=RenderStage.FINALIZE,
                dependencies=["encode_video"],
                inputs={
                    "output_directory": (
                        context.output_directory
                    ),
                    "artifact_directory": (
                        context.artifact_directory
                    ),
                },
                priority=100,
            )
        )

        return RenderGraph(
            production_id=context.production_id,
            version="15.0.0",
            nodes=nodes,
            metadata={
                "builder": "RenderGraphBuilder",
                "source_execution_timeline_version": (
                    timeline.version
                ),
                "node_count": len(nodes),
            },
        )

    def _has_instruction(
        self,
        context: RenderContext,
        instruction_types: set[str],
    ) -> bool:
        return any(
            instruction.instruction_type
            in instruction_types
            for instruction
            in context.execution_timeline.instructions
        )

    def _instructions_by_type(
        self,
        context: RenderContext,
        instruction_types: set[str],
    ) -> dict:
        return {
            "instructions": [
                instruction.to_dict()
                for instruction
                in context.execution_timeline.instructions
                if instruction.instruction_type
                in instruction_types
            ]
        }