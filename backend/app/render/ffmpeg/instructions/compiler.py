from __future__ import annotations

from typing import Any

from app.render.execution.context import RenderContext
from app.render.execution.preloader.models import (
    RenderAssetPreloadResult,
)
from app.render.ffmpeg.instructions.enums import (
    FFmpegInstructionType,
    FFmpegStreamType,
)
from app.render.ffmpeg.instructions.models import (
    FFmpegInputSpec,
    FFmpegInstructionIssue,
    FFmpegInstructionPlan,
    FFmpegRenderInstruction,
)
from app.timeline.compiler.models import (
    TimelineInstruction,
)


class FFmpegInstructionCompiler:
    def compile(
        self,
        context: RenderContext,
        preload_result: RenderAssetPreloadResult,
    ) -> FFmpegInstructionPlan:
        input_specs = self._build_inputs(
            preload_result
        )

        input_map = {
            item.input_id: item
            for item in input_specs
        }

        instructions: list[
            FFmpegRenderInstruction
        ] = []

        issues: list[FFmpegInstructionIssue] = []

        execution_instructions = sorted(
            context.execution_timeline.instructions,
            key=lambda item: (
                item.start_time,
                item.layer,
                item.instruction_type,
                item.instruction_id,
            ),
        )

        for execution_instruction in (
            execution_instructions
        ):
            try:
                compiled = (
                    self._compile_timeline_instruction(
                        instruction=execution_instruction,
                        input_map=input_map,
                        context=context,
                    )
                )

                instructions.extend(compiled)

            except Exception as error:
                issues.append(
                    FFmpegInstructionIssue(
                        level="error",
                        code="instruction_compile_failed",
                        message=str(error),
                        instruction_id=(
                            execution_instruction.instruction_id
                        ),
                        metadata={
                            "instruction_type": (
                                execution_instruction.instruction_type
                            ),
                            "track_type": (
                                execution_instruction.track_type
                            ),
                        },
                    )
                )

        instructions.append(
            self._build_encode_instruction(
                context=context,
                order=len(instructions),
            )
        )

        instructions = self._normalize_order(
            instructions
        )

        return FFmpegInstructionPlan(
            production_id=context.production_id,
            version="15.4.0",
            duration=(
                context.execution_timeline.duration
            ),
            width=(
                context.execution_timeline.width
            ),
            height=(
                context.execution_timeline.height
            ),
            fps=context.execution_timeline.fps,
            inputs=input_specs,
            instructions=instructions,
            issues=issues,
            metadata={
                "compiler": (
                    "FFmpegInstructionCompiler"
                ),
                "input_count": len(input_specs),
                "instruction_count": len(
                    instructions
                ),
                "issue_count": len(issues),
                "source_execution_timeline_version": (
                    context.execution_timeline.version
                ),
            },
        )

    def _build_inputs(
        self,
        preload_result: RenderAssetPreloadResult,
    ) -> list[FFmpegInputSpec]:
        inputs: list[FFmpegInputSpec] = []

        for index, prepared in enumerate(
            preload_result.prepared_inputs
        ):
            inputs.append(
                FFmpegInputSpec(
                    input_id=prepared.input_id,
                    prepared_path=(
                        prepared.prepared_path
                    ),
                    input_type=(
                        prepared.input_type
                    ),
                    ffmpeg_input_index=index,
                    asset_id=prepared.asset_id,
                    duration=prepared.duration,
                    has_video=prepared.has_video,
                    has_audio=prepared.has_audio,
                    metadata={
                        "checksum": (
                            prepared.checksum
                        ),
                        "file_size": (
                            prepared.file_size
                        ),
                        "source_path": (
                            prepared.source_path
                        ),
                    },
                )
            )

        return inputs

    def _compile_timeline_instruction(
        self,
        instruction: TimelineInstruction,
        input_map: dict[str, FFmpegInputSpec],
        context: RenderContext,
    ) -> list[FFmpegRenderInstruction]:
        instruction_type = (
            instruction.instruction_type
        )

        if instruction_type == "place_video":
            return self._compile_primary_video(
                instruction=instruction,
                input_map=input_map,
                context=context,
            )

        if instruction_type == "place_video_overlay":
            return self._compile_video_overlay(
                instruction=instruction,
                input_map=input_map,
                context=context,
            )

        if instruction_type == "place_audio":
            return self._compile_audio(
                instruction=instruction,
                input_map=input_map,
            )

        if instruction_type == "draw_subtitle":
            return self._compile_subtitle(
                instruction=instruction,
            )

        if instruction_type == "apply_effect":
            return self._compile_effect(
                instruction=instruction,
            )

        if instruction_type == "apply_transition":
            return self._compile_transition(
                instruction=instruction,
            )

        return []

    def _compile_primary_video(
        self,
        instruction: TimelineInstruction,
        input_map: dict[str, FFmpegInputSpec],
        context: RenderContext,
    ) -> list[FFmpegRenderInstruction]:
        input_spec = self._require_input(
            instruction=instruction,
            input_map=input_map,
        )

        trim_id = (
            f"ffmpeg_trim_{instruction.instruction_id}"
        )
        scale_id = (
            f"ffmpeg_scale_{instruction.instruction_id}"
        )

        trim_label = (
            f"v_trim_{self._safe_id(instruction.target_id)}"
        )
        scale_label = (
            f"v_scaled_{self._safe_id(instruction.target_id)}"
        )

        return [
            FFmpegRenderInstruction(
                instruction_id=trim_id,
                instruction_type=(
                    FFmpegInstructionType.TRIM_VIDEO
                ),
                stream_type=FFmpegStreamType.VIDEO,
                start_time=instruction.start_time,
                end_time=instruction.end_time,
                source_input_id=input_spec.input_id,
                source_stream_label=(
                    f"{input_spec.ffmpeg_input_index}:v"
                ),
                output_stream_label=trim_label,
                target_id=instruction.target_id,
                layer=instruction.layer,
                parameters={
                    "trim_start": (
                        instruction.start_time
                    ),
                    "trim_duration": (
                        instruction.duration
                    ),
                    "reset_pts": True,
                    "speed": (
                        instruction.parameters.get(
                            "speed"
                        )
                        or 1.0
                    ),
                },
                metadata={
                    "source_timeline_instruction": (
                        instruction.instruction_id
                    ),
                },
            ),
            FFmpegRenderInstruction(
                instruction_id=scale_id,
                instruction_type=(
                    FFmpegInstructionType.SCALE
                ),
                stream_type=FFmpegStreamType.VIDEO,
                start_time=instruction.start_time,
                end_time=instruction.end_time,
                source_stream_label=trim_label,
                output_stream_label=scale_label,
                target_id=instruction.target_id,
                layer=instruction.layer,
                parameters={
                    "width": (
                        context.execution_timeline.width
                    ),
                    "height": (
                        context.execution_timeline.height
                    ),
                    "fit_mode": "cover",
                    "pixel_format": (
                        context.render_config.pixel_format
                    ),
                },
                dependencies=[trim_id],
                metadata={
                    "source_timeline_instruction": (
                        instruction.instruction_id
                    ),
                },
            ),
        ]

    def _compile_video_overlay(
        self,
        instruction: TimelineInstruction,
        input_map: dict[str, FFmpegInputSpec],
        context: RenderContext,
    ) -> list[FFmpegRenderInstruction]:
        input_spec = self._require_input(
            instruction=instruction,
            input_map=input_map,
        )

        trim_id = (
            f"ffmpeg_trim_{instruction.instruction_id}"
        )

        scale_id = (
            f"ffmpeg_scale_{instruction.instruction_id}"
        )

        overlay_id = (
            f"ffmpeg_overlay_{instruction.instruction_id}"
        )

        safe_target = self._safe_id(
            instruction.target_id
        )

        trim_label = f"overlay_trim_{safe_target}"
        scale_label = f"overlay_scaled_{safe_target}"
        output_label = f"overlay_output_{safe_target}"

        return [
            FFmpegRenderInstruction(
                instruction_id=trim_id,
                instruction_type=(
                    FFmpegInstructionType.TRIM_VIDEO
                ),
                stream_type=FFmpegStreamType.VIDEO,
                start_time=instruction.start_time,
                end_time=instruction.end_time,
                source_input_id=input_spec.input_id,
                source_stream_label=(
                    f"{input_spec.ffmpeg_input_index}:v"
                ),
                output_stream_label=trim_label,
                target_id=instruction.target_id,
                layer=instruction.layer,
                parameters={
                    "trim_start": 0.0,
                    "trim_duration": (
                        instruction.duration
                    ),
                    "reset_pts": True,
                    "speed": (
                        instruction.parameters.get(
                            "speed"
                        )
                        or 1.0
                    ),
                },
            ),
            FFmpegRenderInstruction(
                instruction_id=scale_id,
                instruction_type=(
                    FFmpegInstructionType.SCALE
                ),
                stream_type=FFmpegStreamType.VIDEO,
                start_time=instruction.start_time,
                end_time=instruction.end_time,
                source_stream_label=trim_label,
                output_stream_label=scale_label,
                target_id=instruction.target_id,
                layer=instruction.layer,
                parameters={
                    "width": (
                        context.execution_timeline.width
                    ),
                    "height": (
                        context.execution_timeline.height
                    ),
                    "fit_mode": "cover",
                    "opacity": (
                        instruction.parameters.get(
                            "opacity"
                        )
                        or 1.0
                    ),
                },
                dependencies=[trim_id],
            ),
            FFmpegRenderInstruction(
                instruction_id=overlay_id,
                instruction_type=(
                    FFmpegInstructionType.OVERLAY
                ),
                stream_type=FFmpegStreamType.VIDEO,
                start_time=instruction.start_time,
                end_time=instruction.end_time,
                source_stream_label=scale_label,
                output_stream_label=output_label,
                target_id=instruction.target_id,
                layer=instruction.layer,
                parameters={
                    "x": 0,
                    "y": 0,
                    "enable_start": (
                        instruction.start_time
                    ),
                    "enable_end": (
                        instruction.end_time
                    ),
                    "opacity": (
                        instruction.parameters.get(
                            "opacity"
                        )
                        or 1.0
                    ),
                },
                dependencies=[scale_id],
            ),
        ]

    def _compile_audio(
        self,
        instruction: TimelineInstruction,
        input_map: dict[str, FFmpegInputSpec],
    ) -> list[FFmpegRenderInstruction]:
        input_spec = self._require_input(
            instruction=instruction,
            input_map=input_map,
        )

        safe_target = self._safe_id(
            instruction.target_id
        )

        trim_id = (
            f"ffmpeg_audio_trim_"
            f"{instruction.instruction_id}"
        )

        volume_id = (
            f"ffmpeg_volume_"
            f"{instruction.instruction_id}"
        )

        delay_id = (
            f"ffmpeg_audio_delay_"
            f"{instruction.instruction_id}"
        )

        trim_label = f"a_trim_{safe_target}"
        volume_label = f"a_volume_{safe_target}"
        delay_label = f"a_delay_{safe_target}"

        return [
            FFmpegRenderInstruction(
                instruction_id=trim_id,
                instruction_type=(
                    FFmpegInstructionType.TRIM_AUDIO
                ),
                stream_type=FFmpegStreamType.AUDIO,
                start_time=instruction.start_time,
                end_time=instruction.end_time,
                source_input_id=input_spec.input_id,
                source_stream_label=(
                    f"{input_spec.ffmpeg_input_index}:a"
                ),
                output_stream_label=trim_label,
                target_id=instruction.target_id,
                layer=instruction.layer,
                parameters={
                    "trim_start": 0.0,
                    "trim_duration": (
                        instruction.duration
                    ),
                    "reset_pts": True,
                },
            ),
            FFmpegRenderInstruction(
                instruction_id=volume_id,
                instruction_type=(
                    FFmpegInstructionType.VOLUME
                ),
                stream_type=FFmpegStreamType.AUDIO,
                start_time=instruction.start_time,
                end_time=instruction.end_time,
                source_stream_label=trim_label,
                output_stream_label=volume_label,
                target_id=instruction.target_id,
                layer=instruction.layer,
                parameters={
                    "volume": (
                        instruction.parameters.get(
                            "volume"
                        )
                        if instruction.parameters.get(
                            "volume"
                        )
                        is not None
                        else 1.0
                    ),
                },
                dependencies=[trim_id],
            ),
            FFmpegRenderInstruction(
                instruction_id=delay_id,
                instruction_type=(
                    FFmpegInstructionType.AUDIO_DELAY
                ),
                stream_type=FFmpegStreamType.AUDIO,
                start_time=instruction.start_time,
                end_time=instruction.end_time,
                source_stream_label=volume_label,
                output_stream_label=delay_label,
                target_id=instruction.target_id,
                layer=instruction.layer,
                parameters={
                    "delay_ms": round(
                        instruction.start_time * 1000
                    ),
                },
                dependencies=[volume_id],
            ),
        ]

    def _compile_subtitle(
        self,
        instruction: TimelineInstruction,
    ) -> list[FFmpegRenderInstruction]:
        content = (
            instruction.parameters.get("content")
            or ""
        )

        return [
            FFmpegRenderInstruction(
                instruction_id=(
                    f"ffmpeg_subtitle_"
                    f"{instruction.instruction_id}"
                ),
                instruction_type=(
                    FFmpegInstructionType.DRAW_SUBTITLE
                ),
                stream_type=(
                    FFmpegStreamType.SUBTITLE
                ),
                start_time=instruction.start_time,
                end_time=instruction.end_time,
                target_id=instruction.target_id,
                layer=instruction.layer,
                parameters={
                    "text": content,
                    "enable_start": (
                        instruction.start_time
                    ),
                    "enable_end": (
                        instruction.end_time
                    ),
                    "font_family": (
                        instruction.metadata.get(
                            "font_family"
                        )
                        or "Noto Sans"
                    ),
                    "font_size": (
                        instruction.metadata.get(
                            "font_size"
                        )
                        or 54
                    ),
                    "font_color": (
                        instruction.metadata.get(
                            "text_color"
                        )
                        or "#FFFFFF"
                    ),
                    "stroke_color": (
                        instruction.metadata.get(
                            "stroke_color"
                        )
                        or "#000000"
                    ),
                    "stroke_width": (
                        instruction.metadata.get(
                            "stroke_width"
                        )
                        or 3
                    ),
                    "position": (
                        instruction.metadata.get(
                            "position"
                        )
                        or "bottom"
                    ),
                    "highlight_words": (
                        instruction.metadata.get(
                            "highlight_words"
                        )
                        or []
                    ),
                },
                metadata={
                    "source_timeline_instruction": (
                        instruction.instruction_id
                    ),
                },
            )
        ]

    def _compile_effect(
        self,
        instruction: TimelineInstruction,
    ) -> list[FFmpegRenderInstruction]:
        return [
            FFmpegRenderInstruction(
                instruction_id=(
                    f"ffmpeg_effect_"
                    f"{instruction.instruction_id}"
                ),
                instruction_type=(
                    FFmpegInstructionType.APPLY_VIDEO_EFFECT
                ),
                stream_type=FFmpegStreamType.VIDEO,
                start_time=instruction.start_time,
                end_time=instruction.end_time,
                target_id=instruction.target_id,
                layer=instruction.layer,
                parameters=dict(
                    instruction.parameters
                ),
                metadata={
                    "source_timeline_instruction": (
                        instruction.instruction_id
                    ),
                },
            )
        ]

    def _compile_transition(
        self,
        instruction: TimelineInstruction,
    ) -> list[FFmpegRenderInstruction]:
        return [
            FFmpegRenderInstruction(
                instruction_id=(
                    f"ffmpeg_transition_"
                    f"{instruction.instruction_id}"
                ),
                instruction_type=(
                    FFmpegInstructionType.APPLY_TRANSITION
                ),
                stream_type=FFmpegStreamType.VIDEO,
                start_time=instruction.start_time,
                end_time=instruction.end_time,
                target_id=instruction.target_id,
                layer=instruction.layer,
                parameters=dict(
                    instruction.parameters
                ),
                metadata={
                    "source_timeline_instruction": (
                        instruction.instruction_id
                    ),
                },
            )
        ]

    def _build_encode_instruction(
        self,
        context: RenderContext,
        order: int,
    ) -> FFmpegRenderInstruction:
        return FFmpegRenderInstruction(
            instruction_id="ffmpeg_encode_output",
            instruction_type=(
                FFmpegInstructionType.ENCODE
            ),
            stream_type=FFmpegStreamType.OUTPUT,
            start_time=0.0,
            end_time=(
                context.execution_timeline.duration
            ),
            layer=1000,
            order=order,
            parameters={
                "video_codec": (
                    context.render_config.video_codec
                ),
                "audio_codec": (
                    context.render_config.audio_codec
                ),
                "pixel_format": (
                    context.render_config.pixel_format
                ),
                "preset": (
                    context.render_config.preset
                ),
                "crf": context.render_config.crf,
                "video_bitrate": (
                    context.render_config.video_bitrate
                ),
                "audio_bitrate": (
                    context.render_config.audio_bitrate
                ),
                "width": (
                    context.render_config.width
                ),
                "height": (
                    context.render_config.height
                ),
                "fps": context.render_config.fps,
                "output_path": (
                    f"{context.output_directory}/"
                    "final.mp4"
                ),
                "overwrite": (
                    context.render_config.overwrite
                ),
            },
        )

    def _require_input(
        self,
        instruction: TimelineInstruction,
        input_map: dict[str, FFmpegInputSpec],
    ) -> FFmpegInputSpec:
        if not instruction.input_id:
            raise ValueError(
                "Timeline media instruction has no input_id: "
                f"{instruction.instruction_id}"
            )

        input_spec = input_map.get(
            instruction.input_id
        )

        if input_spec is None:
            raise KeyError(
                "Prepared input not found for "
                f"input_id={instruction.input_id}"
            )

        return input_spec

    def _normalize_order(
        self,
        instructions: list[FFmpegRenderInstruction],
    ) -> list[FFmpegRenderInstruction]:
        ordered = sorted(
            instructions,
            key=lambda item: (
                item.start_time,
                item.layer,
                self._type_priority(
                    item.instruction_type
                ),
                item.instruction_id,
            ),
        )

        for index, item in enumerate(ordered):
            item.order = index

        return ordered

    def _type_priority(
        self,
        instruction_type: Any,
    ) -> int:
        value = (
            instruction_type.value
            if hasattr(instruction_type, "value")
            else str(instruction_type)
        )

        mapping = {
            FFmpegInstructionType.TRIM_VIDEO.value: 10,
            FFmpegInstructionType.TRIM_AUDIO.value: 10,
            FFmpegInstructionType.SCALE.value: 20,
            FFmpegInstructionType.CROP.value: 25,
            FFmpegInstructionType.VOLUME.value: 30,
            FFmpegInstructionType.AUDIO_DELAY.value: 40,
            FFmpegInstructionType.OVERLAY.value: 50,
            FFmpegInstructionType.APPLY_VIDEO_EFFECT.value: 60,
            FFmpegInstructionType.APPLY_TRANSITION.value: 70,
            FFmpegInstructionType.DRAW_SUBTITLE.value: 80,
            FFmpegInstructionType.AUDIO_MIX.value: 90,
            FFmpegInstructionType.ENCODE.value: 1000,
        }

        return mapping.get(value, 500)

    def _safe_id(
        self,
        value: str | None,
    ) -> str:
        if not value:
            return "unknown"

        return "".join(
            character
            if character.isalnum()
            else "_"
            for character in value
        )