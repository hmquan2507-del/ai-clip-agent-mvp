from __future__ import annotations

from collections import defaultdict
from typing import Any

from app.render.ffmpeg.filtergraph.models import (
    FFmpegFilterChain,
    FFmpegFilterGraph,
    FFmpegFilterGraphIssue,
    FFmpegInputArgument,
)
from app.render.ffmpeg.instructions import (
    FFmpegInstructionPlan,
    FFmpegInstructionType,
    FFmpegRenderInstruction,
)


class FFmpegFilterGraphBuilder:
    def build(
        self,
        plan: FFmpegInstructionPlan,
    ) -> FFmpegFilterGraph:
        issues: list[FFmpegFilterGraphIssue] = []

        input_arguments = self._build_input_arguments(
            plan
        )

        chains: list[FFmpegFilterChain] = []

        primary_video_instructions = (
            self._instructions_by_type(
                plan,
                FFmpegInstructionType.TRIM_VIDEO.value,
            )
        )

        primary_video_instructions = [
            item
            for item in primary_video_instructions
            if self._is_primary_video(item)
        ]

        overlay_trim_instructions = [
            item
            for item in self._instructions_by_type(
                plan,
                FFmpegInstructionType.TRIM_VIDEO.value,
            )
            if not self._is_primary_video(item)
        ]

        primary_output_label = (
            self._build_primary_video_pipeline(
                plan=plan,
                trim_instructions=primary_video_instructions,
                chains=chains,
                issues=issues,
            )
        )

        if primary_output_label is None:
            issues.append(
                FFmpegFilterGraphIssue(
                    level="error",
                    code="primary_video_missing",
                    message=(
                        "No primary video stream could be "
                        "constructed."
                    ),
                )
            )

        current_video_label = primary_output_label

        if current_video_label is not None:
            current_video_label = (
                self._build_overlay_pipeline(
                    plan=plan,
                    overlay_trim_instructions=(
                        overlay_trim_instructions
                    ),
                    base_video_label=(
                        current_video_label
                    ),
                    chains=chains,
                )
            )

            current_video_label = (
                self._build_effect_pipeline(
                    plan=plan,
                    current_video_label=(
                        current_video_label
                    ),
                    chains=chains,
                )
            )

            current_video_label = (
                self._build_transition_pipeline(
                    plan=plan,
                    current_video_label=(
                        current_video_label
                    ),
                    chains=chains,
                )
            )

            current_video_label = (
                self._build_subtitle_pipeline(
                    plan=plan,
                    current_video_label=(
                        current_video_label
                    ),
                    chains=chains,
                )
            )

        audio_output_label = self._build_audio_pipeline(
            plan=plan,
            chains=chains,
        )

        encode_instruction = self._encode_instruction(
            plan
        )

        output_path = str(
            encode_instruction.parameters.get(
                "output_path",
                "storage/render/output/final.mp4",
            )
        )

        map_arguments: list[str] = []

        if current_video_label:
            map_arguments.extend(
                ["-map", f"[{current_video_label}]"]
            )

        if audio_output_label:
            map_arguments.extend(
                ["-map", f"[{audio_output_label}]"]
            )

        output_arguments = (
            self._build_output_arguments(
                encode_instruction
            )
        )

        ordered_chains = sorted(
            chains,
            key=lambda item: (
                item.order,
                item.chain_id,
            ),
        )

        filter_complex = ";".join(
            chain.filter_text
            for chain in ordered_chains
            if chain.filter_text
        )

        return FFmpegFilterGraph(
            production_id=plan.production_id,
            version="15.5.0",
            input_arguments=input_arguments,
            chains=ordered_chains,
            filter_complex=filter_complex,
            video_output_label=current_video_label,
            audio_output_label=audio_output_label,
            map_arguments=map_arguments,
            output_arguments=output_arguments,
            output_path=output_path,
            issues=issues,
            metadata={
                "builder": "FFmpegFilterGraphBuilder",
                "source_instruction_plan_version": (
                    plan.version
                ),
                "input_count": len(input_arguments),
                "chain_count": len(ordered_chains),
                "has_video_output": (
                    current_video_label is not None
                ),
                "has_audio_output": (
                    audio_output_label is not None
                ),
                "duration": plan.duration,
                "width": plan.width,
                "height": plan.height,
                "fps": plan.fps,
            },
        )

    def _build_input_arguments(
        self,
        plan: FFmpegInstructionPlan,
    ) -> list[FFmpegInputArgument]:
        values: list[FFmpegInputArgument] = []

        for item in sorted(
            plan.inputs,
            key=lambda value: (
                value.ffmpeg_input_index
            ),
        ):
            values.append(
                FFmpegInputArgument(
                    input_id=item.input_id,
                    input_index=(
                        item.ffmpeg_input_index
                    ),
                    prepared_path=item.prepared_path,
                    arguments=[
                        "-i",
                        item.prepared_path,
                    ],
                    metadata={
                        "input_type": item.input_type,
                        "asset_id": item.asset_id,
                        "duration": item.duration,
                        "has_video": item.has_video,
                        "has_audio": item.has_audio,
                    },
                )
            )

        return values

    def _build_primary_video_pipeline(
        self,
        plan: FFmpegInstructionPlan,
        trim_instructions: list[
            FFmpegRenderInstruction
        ],
        chains: list[FFmpegFilterChain],
        issues: list[FFmpegFilterGraphIssue],
    ) -> str | None:
        if not trim_instructions:
            return None

        segment_labels: list[str] = []

        ordered = sorted(
            trim_instructions,
            key=lambda item: (
                item.start_time,
                item.order,
            ),
        )

        for index, trim_instruction in enumerate(
            ordered
        ):
            scale_instruction = (
                self._dependent_instruction(
                    plan=plan,
                    dependency_id=(
                        trim_instruction.instruction_id
                    ),
                    instruction_type=(
                        FFmpegInstructionType.SCALE.value
                    ),
                )
            )

            if scale_instruction is None:
                issues.append(
                    FFmpegFilterGraphIssue(
                        level="error",
                        code="primary_scale_missing",
                        message=(
                            "Primary video trim has no "
                            "dependent scale instruction."
                        ),
                        chain_id=(
                            trim_instruction.instruction_id
                        ),
                    )
                )
                continue

            trim_label = f"primary_trim_{index}"
            segment_label = f"primary_segment_{index}"

            source_label = self._label(
                trim_instruction.source_stream_label
            )

            trim_start = float(
                trim_instruction.parameters.get(
                    "trim_start",
                    0.0,
                )
            )

            trim_duration = float(
                trim_instruction.parameters.get(
                    "trim_duration",
                    trim_instruction.duration,
                )
            )

            speed = float(
                trim_instruction.parameters.get(
                    "speed",
                    1.0,
                )
                or 1.0
            )

            if speed <= 0:
                speed = 1.0

            trim_filter = (
                f"{source_label}"
                f"trim=start={self._number(trim_start)}:"
                f"duration={self._number(trim_duration)},"
                f"setpts=(PTS-STARTPTS)/"
                f"{self._number(speed)}"
                f"[{trim_label}]"
            )

            chains.append(
                FFmpegFilterChain(
                    chain_id=(
                        f"primary_trim_chain_{index}"
                    ),
                    filter_text=trim_filter,
                    input_labels=[
                        trim_instruction.source_stream_label
                        or ""
                    ],
                    output_label=trim_label,
                    stage="primary_trim",
                    order=100 + index * 10,
                    metadata={
                        "timeline_target_id": (
                            trim_instruction.target_id
                        ),
                    },
                )
            )

            width = int(
                scale_instruction.parameters.get(
                    "width",
                    plan.width,
                )
            )

            height = int(
                scale_instruction.parameters.get(
                    "height",
                    plan.height,
                )
            )

            scale_filter = (
                f"[{trim_label}]"
                f"scale={width}:{height}:"
                f"force_original_aspect_ratio=increase,"
                f"crop={width}:{height},"
                f"setsar=1,"
                f"fps={self._number(plan.fps)},"
                f"format=yuv420p"
                f"[{segment_label}]"
            )

            chains.append(
                FFmpegFilterChain(
                    chain_id=(
                        f"primary_scale_chain_{index}"
                    ),
                    filter_text=scale_filter,
                    input_labels=[trim_label],
                    output_label=segment_label,
                    stage="primary_scale",
                    order=101 + index * 10,
                )
            )

            segment_labels.append(segment_label)

        if not segment_labels:
            return None

        if len(segment_labels) == 1:
            output_label = "primary_video"

            chains.append(
                FFmpegFilterChain(
                    chain_id="primary_copy_chain",
                    filter_text=(
                        f"[{segment_labels[0]}]"
                        f"null[{output_label}]"
                    ),
                    input_labels=[
                        segment_labels[0]
                    ],
                    output_label=output_label,
                    stage="primary_concat",
                    order=500,
                )
            )

            return output_label

        concat_inputs = "".join(
            f"[{label}]"
            for label in segment_labels
        )

        output_label = "primary_video"

        chains.append(
            FFmpegFilterChain(
                chain_id="primary_concat_chain",
                filter_text=(
                    f"{concat_inputs}"
                    f"concat=n={len(segment_labels)}:"
                    f"v=1:a=0"
                    f"[{output_label}]"
                ),
                input_labels=segment_labels,
                output_label=output_label,
                stage="primary_concat",
                order=500,
            )
        )

        return output_label

    def _build_overlay_pipeline(
        self,
        plan: FFmpegInstructionPlan,
        overlay_trim_instructions: list[
            FFmpegRenderInstruction
        ],
        base_video_label: str,
        chains: list[FFmpegFilterChain],
    ) -> str:
        current_label = base_video_label

        ordered = sorted(
            overlay_trim_instructions,
            key=lambda item: (
                item.start_time,
                item.layer,
                item.order,
            ),
        )

        for index, trim_instruction in enumerate(
            ordered
        ):
            scale_instruction = (
                self._dependent_instruction(
                    plan=plan,
                    dependency_id=(
                        trim_instruction.instruction_id
                    ),
                    instruction_type=(
                        FFmpegInstructionType.SCALE.value
                    ),
                )
            )

            if scale_instruction is None:
                continue

            overlay_instruction = (
                self._dependent_instruction(
                    plan=plan,
                    dependency_id=(
                        scale_instruction.instruction_id
                    ),
                    instruction_type=(
                        FFmpegInstructionType.OVERLAY.value
                    ),
                )
            )

            if overlay_instruction is None:
                continue

            trim_label = f"broll_trim_{index}"
            scaled_label = f"broll_scaled_{index}"
            output_label = f"video_overlay_{index}"

            source_label = self._label(
                trim_instruction.source_stream_label
            )

            trim_start = float(
                trim_instruction.parameters.get(
                    "trim_start",
                    0.0,
                )
            )

            trim_duration = float(
                trim_instruction.parameters.get(
                    "trim_duration",
                    trim_instruction.duration,
                )
            )

            chains.append(
                FFmpegFilterChain(
                    chain_id=f"broll_trim_chain_{index}",
                    filter_text=(
                        f"{source_label}"
                        f"trim=start="
                        f"{self._number(trim_start)}:"
                        f"duration="
                        f"{self._number(trim_duration)},"
                        f"setpts=PTS-STARTPTS"
                        f"[{trim_label}]"
                    ),
                    input_labels=[
                        trim_instruction.source_stream_label
                        or ""
                    ],
                    output_label=trim_label,
                    stage="broll_trim",
                    order=600 + index * 10,
                )
            )

            width = int(
                scale_instruction.parameters.get(
                    "width",
                    plan.width,
                )
            )

            height = int(
                scale_instruction.parameters.get(
                    "height",
                    plan.height,
                )
            )

            opacity = float(
                scale_instruction.parameters.get(
                    "opacity",
                    1.0,
                )
            )

            scale_filters = (
                f"scale={width}:{height}:"
                f"force_original_aspect_ratio=increase,"
                f"crop={width}:{height},"
                f"setsar=1,"
                f"format=rgba"
            )

            if opacity < 1.0:
                scale_filters += (
                    f",colorchannelmixer="
                    f"aa={self._number(opacity)}"
                )

            chains.append(
                FFmpegFilterChain(
                    chain_id=f"broll_scale_chain_{index}",
                    filter_text=(
                        f"[{trim_label}]"
                        f"{scale_filters}"
                        f"[{scaled_label}]"
                    ),
                    input_labels=[trim_label],
                    output_label=scaled_label,
                    stage="broll_scale",
                    order=601 + index * 10,
                )
            )

            enable_start = float(
                overlay_instruction.parameters.get(
                    "enable_start",
                    overlay_instruction.start_time,
                )
            )

            enable_end = float(
                overlay_instruction.parameters.get(
                    "enable_end",
                    overlay_instruction.end_time,
                )
            )

            x = overlay_instruction.parameters.get(
                "x",
                0,
            )

            y = overlay_instruction.parameters.get(
                "y",
                0,
            )

            delayed_overlay_label = (
                f"broll_delayed_{index}"
            )

            chains.append(
                FFmpegFilterChain(
                    chain_id=f"broll_delay_chain_{index}",
                    filter_text=(
                        f"[{scaled_label}]"
                        f"setpts=PTS+"
                        f"{self._number(enable_start)}"
                        f"/TB"
                        f"[{delayed_overlay_label}]"
                    ),
                    input_labels=[scaled_label],
                    output_label=delayed_overlay_label,
                    stage="broll_timing",
                    order=602 + index * 10,
                )
            )

            chains.append(
                FFmpegFilterChain(
                    chain_id=f"overlay_chain_{index}",
                    filter_text=(
                        f"[{current_label}]"
                        f"[{delayed_overlay_label}]"
                        f"overlay="
                        f"x={x}:y={y}:"
                        f"enable='between(t,"
                        f"{self._number(enable_start)},"
                        f"{self._number(enable_end)})':"
                        f"eof_action=pass"
                        f"[{output_label}]"
                    ),
                    input_labels=[
                        current_label,
                        delayed_overlay_label,
                    ],
                    output_label=output_label,
                    stage="overlay",
                    order=603 + index * 10,
                )
            )

            current_label = output_label

        return current_label

    def _build_effect_pipeline(
        self,
        plan: FFmpegInstructionPlan,
        current_video_label: str,
        chains: list[FFmpegFilterChain],
    ) -> str:
        current_label = current_video_label

        effects = self._instructions_by_type(
            plan,
            FFmpegInstructionType.APPLY_VIDEO_EFFECT.value,
        )

        for index, instruction in enumerate(
            sorted(
                effects,
                key=lambda item: item.order,
            )
        ):
            output_label = f"video_effect_{index}"

            movement_type = str(
                instruction.parameters.get(
                    "movement_type",
                    "",
                )
            )

            start_time = self._number(
                instruction.start_time
            )

            end_time = self._number(
                instruction.end_time
            )

            if movement_type in {
                "ken_burns_zoom_in",
                "slow_push_in",
                "cta_scale_up",
            }:
                scale_to = float(
                    instruction.parameters.get(
                        "scale_to",
                        1.08,
                    )
                )

                zoom_expression = (
                    "min("
                    f"1+({self._number(scale_to - 1.0)})"
                    f"*on/"
                    f"max(1,{self._number(instruction.duration * plan.fps)}),"
                    f"{self._number(scale_to)}"
                    ")"
                )

                filter_text = (
                    f"[{current_label}]"
                    f"zoompan="
                    f"z='{zoom_expression}':"
                    f"x='iw/2-(iw/zoom/2)':"
                    f"y='ih/2-(ih/zoom/2)':"
                    f"d=1:"
                    f"s={plan.width}x{plan.height}:"
                    f"fps={self._number(plan.fps)},"
                    f"setpts=PTS-STARTPTS"
                    f"[{output_label}]"
                )
            else:
                filter_text = (
                    f"[{current_label}]"
                    f"null"
                    f"[{output_label}]"
                )

            chains.append(
                FFmpegFilterChain(
                    chain_id=f"effect_chain_{index}",
                    filter_text=filter_text,
                    input_labels=[current_label],
                    output_label=output_label,
                    stage="effect",
                    order=1000 + index,
                    metadata={
                        "target_id": instruction.target_id,
                        "enable_start": start_time,
                        "enable_end": end_time,
                    },
                )
            )

            current_label = output_label

        return current_label

    def _build_transition_pipeline(
        self,
        plan: FFmpegInstructionPlan,
        current_video_label: str,
        chains: list[FFmpegFilterChain],
    ) -> str:
        current_label = current_video_label

        transitions = self._instructions_by_type(
            plan,
            FFmpegInstructionType.APPLY_TRANSITION.value,
        )

        for index, instruction in enumerate(
            sorted(
                transitions,
                key=lambda item: item.order,
            )
        ):
            output_label = (
                f"video_transition_{index}"
            )

            transition_type = str(
                instruction.parameters.get(
                    "transition_type",
                    "",
                )
            )

            if transition_type in {
                "smooth_cut",
                "clean_cut",
            }:
                filter_text = (
                    f"[{current_label}]"
                    f"fade=t=in:"
                    f"st={self._number(instruction.start_time)}:"
                    f"d={self._number(instruction.duration)}"
                    f"[{output_label}]"
                )
            elif transition_type == "impact_cut":
                filter_text = (
                    f"[{current_label}]"
                    f"eq=contrast=1.08:"
                    f"brightness=0.01"
                    f"[{output_label}]"
                )
            else:
                filter_text = (
                    f"[{current_label}]"
                    f"null"
                    f"[{output_label}]"
                )

            chains.append(
                FFmpegFilterChain(
                    chain_id=(
                        f"transition_chain_{index}"
                    ),
                    filter_text=filter_text,
                    input_labels=[current_label],
                    output_label=output_label,
                    stage="transition",
                    order=1100 + index,
                    metadata={
                        "target_id": instruction.target_id,
                        "transition_type": transition_type,
                    },
                )
            )

            current_label = output_label

        return current_label

    def _build_subtitle_pipeline(
        self,
        plan: FFmpegInstructionPlan,
        current_video_label: str,
        chains: list[FFmpegFilterChain],
    ) -> str:
        current_label = current_video_label

        subtitles = self._instructions_by_type(
            plan,
            FFmpegInstructionType.DRAW_SUBTITLE.value,
        )

        for index, instruction in enumerate(
            sorted(
                subtitles,
                key=lambda item: (
                    item.start_time,
                    item.order,
                ),
            )
        ):
            output_label = f"subtitle_video_{index}"

            text = self._escape_drawtext(
                str(
                    instruction.parameters.get(
                        "text",
                        "",
                    )
                )
            )

            font_size = int(
                instruction.parameters.get(
                    "font_size",
                    54,
                )
            )

            font_color = self._normalize_color(
                str(
                    instruction.parameters.get(
                        "font_color",
                        "FFFFFF",
                    )
                )
            )

            stroke_color = self._normalize_color(
                str(
                    instruction.parameters.get(
                        "stroke_color",
                        "000000",
                    )
                )
            )

            stroke_width = int(
                instruction.parameters.get(
                    "stroke_width",
                    3,
                )
            )

            start_time = self._number(
                instruction.start_time
            )

            end_time = self._number(
                instruction.end_time
            )

            filter_text = (
                f"[{current_label}]"
                f"drawtext="
                f"text='{text}':"
                f"fontsize={font_size}:"
                f"fontcolor={font_color}:"
                f"borderw={stroke_width}:"
                f"bordercolor={stroke_color}:"
                f"x=(w-text_w)/2:"
                f"y=h-text_h-120:"
                f"enable='between(t,"
                f"{start_time},{end_time})'"
                f"[{output_label}]"
            )

            chains.append(
                FFmpegFilterChain(
                    chain_id=f"subtitle_chain_{index}",
                    filter_text=filter_text,
                    input_labels=[current_label],
                    output_label=output_label,
                    stage="subtitle",
                    order=1200 + index,
                    metadata={
                        "target_id": instruction.target_id,
                    },
                )
            )

            current_label = output_label

        return current_label

    def _build_audio_pipeline(
        self,
        plan: FFmpegInstructionPlan,
        chains: list[FFmpegFilterChain],
    ) -> str | None:
        trim_instructions = (
            self._instructions_by_type(
                plan,
                FFmpegInstructionType.TRIM_AUDIO.value,
            )
        )

        if not trim_instructions:
            return None

        output_labels: list[str] = []

        ordered = sorted(
            trim_instructions,
            key=lambda item: (
                item.start_time,
                item.layer,
                item.order,
            ),
        )

        for index, trim_instruction in enumerate(
            ordered
        ):
            volume_instruction = (
                self._dependent_instruction(
                    plan=plan,
                    dependency_id=(
                        trim_instruction.instruction_id
                    ),
                    instruction_type=(
                        FFmpegInstructionType.VOLUME.value
                    ),
                )
            )

            if volume_instruction is None:
                continue

            delay_instruction = (
                self._dependent_instruction(
                    plan=plan,
                    dependency_id=(
                        volume_instruction.instruction_id
                    ),
                    instruction_type=(
                        FFmpegInstructionType.AUDIO_DELAY.value
                    ),
                )
            )

            if delay_instruction is None:
                continue

            trim_label = f"audio_trim_{index}"
            volume_label = f"audio_volume_{index}"
            delay_label = f"audio_delay_{index}"

            source_label = self._label(
                trim_instruction.source_stream_label
            )

            trim_start = float(
                trim_instruction.parameters.get(
                    "trim_start",
                    0.0,
                )
            )

            trim_duration = float(
                trim_instruction.parameters.get(
                    "trim_duration",
                    trim_instruction.duration,
                )
            )

            chains.append(
                FFmpegFilterChain(
                    chain_id=f"audio_trim_chain_{index}",
                    filter_text=(
                        f"{source_label}"
                        f"atrim=start="
                        f"{self._number(trim_start)}:"
                        f"duration="
                        f"{self._number(trim_duration)},"
                        f"asetpts=PTS-STARTPTS"
                        f"[{trim_label}]"
                    ),
                    input_labels=[
                        trim_instruction.source_stream_label
                        or ""
                    ],
                    output_label=trim_label,
                    stage="audio_trim",
                    order=2000 + index * 10,
                )
            )

            volume = float(
                volume_instruction.parameters.get(
                    "volume",
                    1.0,
                )
            )

            chains.append(
                FFmpegFilterChain(
                    chain_id=f"audio_volume_chain_{index}",
                    filter_text=(
                        f"[{trim_label}]"
                        f"volume={self._number(volume)}"
                        f"[{volume_label}]"
                    ),
                    input_labels=[trim_label],
                    output_label=volume_label,
                    stage="audio_volume",
                    order=2001 + index * 10,
                )
            )

            delay_ms = int(
                delay_instruction.parameters.get(
                    "delay_ms",
                    0,
                )
            )

            chains.append(
                FFmpegFilterChain(
                    chain_id=f"audio_delay_chain_{index}",
                    filter_text=(
                        f"[{volume_label}]"
                        f"adelay={delay_ms}|{delay_ms}"
                        f"[{delay_label}]"
                    ),
                    input_labels=[volume_label],
                    output_label=delay_label,
                    stage="audio_delay",
                    order=2002 + index * 10,
                )
            )

            output_labels.append(delay_label)

        if not output_labels:
            return None

        if len(output_labels) == 1:
            output_label = "audio_output"

            chains.append(
                FFmpegFilterChain(
                    chain_id="audio_copy_chain",
                    filter_text=(
                        f"[{output_labels[0]}]"
                        f"anull[{output_label}]"
                    ),
                    input_labels=[
                        output_labels[0]
                    ],
                    output_label=output_label,
                    stage="audio_mix",
                    order=3000,
                )
            )

            return output_label

        mix_inputs = "".join(
            f"[{label}]"
            for label in output_labels
        )

        output_label = "audio_output"

        chains.append(
            FFmpegFilterChain(
                chain_id="audio_mix_chain",
                filter_text=(
                    f"{mix_inputs}"
                    f"amix=inputs={len(output_labels)}:"
                    f"duration=longest:"
                    f"dropout_transition=0,"
                    f"atrim=duration="
                    f"{self._number(plan.duration)},"
                    f"asetpts=PTS-STARTPTS"
                    f"[{output_label}]"
                ),
                input_labels=output_labels,
                output_label=output_label,
                stage="audio_mix",
                order=3000,
            )
        )

        return output_label

    def _build_output_arguments(
        self,
        encode_instruction: FFmpegRenderInstruction,
    ) -> list[str]:
        parameters = encode_instruction.parameters

        arguments = [
            "-c:v",
            str(
                parameters.get(
                    "video_codec",
                    "libx264",
                )
            ),
            "-pix_fmt",
            str(
                parameters.get(
                    "pixel_format",
                    "yuv420p",
                )
            ),
            "-preset",
            str(
                parameters.get(
                    "preset",
                    "medium",
                )
            ),
            "-crf",
            str(
                parameters.get(
                    "crf",
                    23,
                )
            ),
            "-c:a",
            str(
                parameters.get(
                    "audio_codec",
                    "aac",
                )
            ),
            "-b:a",
            str(
                parameters.get(
                    "audio_bitrate",
                    "192k",
                )
            ),
            "-r",
            str(
                parameters.get(
                    "fps",
                    30,
                )
            ),
            "-t",
            self._number(
                encode_instruction.duration
            ),
            "-movflags",
            "+faststart",
        ]

        video_bitrate = parameters.get(
            "video_bitrate"
        )

        if video_bitrate:
            arguments.extend(
                [
                    "-b:v",
                    str(video_bitrate),
                ]
            )

        return arguments

    def _encode_instruction(
        self,
        plan: FFmpegInstructionPlan,
    ) -> FFmpegRenderInstruction:
        matches = self._instructions_by_type(
            plan,
            FFmpegInstructionType.ENCODE.value,
        )

        if len(matches) != 1:
            raise ValueError(
                "FFmpeg instruction plan must contain "
                "exactly one encode instruction."
            )

        return matches[0]

    def _instructions_by_type(
        self,
        plan: FFmpegInstructionPlan,
        instruction_type: str,
    ) -> list[FFmpegRenderInstruction]:
        return [
            item
            for item in plan.instructions
            if self._value(
                item.instruction_type
            )
            == instruction_type
        ]

    def _dependent_instruction(
        self,
        plan: FFmpegInstructionPlan,
        dependency_id: str,
        instruction_type: str,
    ) -> FFmpegRenderInstruction | None:
        return next(
            (
                item
                for item in plan.instructions
                if dependency_id
                in item.dependencies
                and self._value(
                    item.instruction_type
                )
                == instruction_type
            ),
            None,
        )

    def _is_primary_video(
        self,
        instruction: FFmpegRenderInstruction,
    ) -> bool:
        source = str(
            instruction.metadata.get(
                "source_timeline_instruction",
                "",
            )
        )

        return (
            "clip_instruction_seg_"
            in source
            and source.endswith("_source")
        )

    def _label(
        self,
        value: str | None,
    ) -> str:
        if not value:
            raise ValueError(
                "FFmpeg stream label is missing."
            )

        value = value.strip()

        if value.startswith("["):
            return value

        return f"[{value}]"

    def _escape_drawtext(
        self,
        value: str,
    ) -> str:
        return (
            value
            .replace("\\", "\\\\")
            .replace(":", "\\:")
            .replace("'", "\\'")
            .replace("%", "\\%")
            .replace(",", "\\,")
            .replace("[", "\\[")
            .replace("]", "\\]")
            .replace("\n", "\\n")
        )

    def _normalize_color(
        self,
        value: str,
    ) -> str:
        normalized = value.strip()

        if normalized.startswith("#"):
            normalized = normalized[1:]

        return normalized or "FFFFFF"

    def _number(
        self,
        value: float | int,
    ) -> str:
        number = float(value)

        if number.is_integer():
            return str(int(number))

        return (
            f"{number:.6f}"
            .rstrip("0")
            .rstrip(".")
        )

    def _value(
        self,
        value: Any,
    ) -> str:
        return (
            value.value
            if hasattr(value, "value")
            else str(value)
        )