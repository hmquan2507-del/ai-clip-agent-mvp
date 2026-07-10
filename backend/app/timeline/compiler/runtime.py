from __future__ import annotations

from pathlib import Path

from app.timeline.compiler.models import (
    ExecutionTimeline,
    TimelineCompilerIssue,
    TimelineInput,
    TimelineInstruction,
)
from app.timeline.finalizer.models import FinalTimeline


class TimelineCompilerRuntime:
    def compile(
        self,
        timeline: FinalTimeline,
        source_video_path: str | None = None,
    ) -> ExecutionTimeline:
        inputs: list[TimelineInput] = []
        instructions: list[TimelineInstruction] = []
        issues: list[TimelineCompilerIssue] = []

        input_index: dict[str, str] = {}

        for track in timeline.tracks:
            for clip in track.clips:
                local_path = clip.local_path

                if (
                    clip.track_type == "video_primary"
                    and not local_path
                    and source_video_path
                ):
                    local_path = source_video_path

                input_id = None

                if self._requires_media_input(clip.track_type):
                    if not local_path:
                        issues.append(
                            TimelineCompilerIssue(
                                level="error",
                                code="missing_media_path",
                                message=(
                                    "Media clip requires local_path "
                                    "before rendering."
                                ),
                                source_id=clip.clip_id,
                                metadata={
                                    "track_type": clip.track_type,
                                },
                            )
                        )
                    else:
                        input_id = self._get_or_create_input(
                            inputs=inputs,
                            input_index=input_index,
                            local_path=local_path,
                            input_type=self._input_type(
                                clip.track_type
                            ),
                            asset_id=clip.asset_id,
                            metadata={
                                "clip_id": clip.clip_id,
                                "track_type": clip.track_type,
                            },
                        )

                instructions.append(
                    TimelineInstruction(
                        instruction_id=(
                            f"clip_instruction_{clip.clip_id}"
                        ),
                        instruction_type=self._instruction_type(
                            clip.track_type
                        ),
                        track_type=clip.track_type,
                        start_time=clip.start_time,
                        end_time=clip.end_time,
                        layer=clip.layer,
                        input_id=input_id,
                        target_id=clip.clip_id,
                        parameters={
                            "content": clip.content,
                            "volume": clip.volume,
                            "opacity": clip.opacity,
                            "speed": clip.speed,
                        },
                        metadata={
                            **clip.metadata,
                            "source_clip_id": clip.clip_id,
                        },
                    )
                )

        instructions.extend(
            self._compile_effects(timeline)
        )

        instructions.extend(
            self._compile_transitions(timeline)
        )

        instructions = self._sort_instructions(
            instructions
        )

        issues.extend(
            self._validate_instructions(
                timeline=timeline,
                instructions=instructions,
            )
        )

        has_errors = any(
            issue.level == "error"
            for issue in issues
        )

        return ExecutionTimeline(
            production_id=timeline.production_id,
            version="14.12.0",
            duration=timeline.duration,
            width=timeline.width,
            height=timeline.height,
            fps=timeline.fps,
            inputs=inputs,
            instructions=instructions,
            issues=issues,
            metadata={
                "runtime": "TimelineCompilerRuntime",
                "source_timeline_version": timeline.version,
                "input_count": len(inputs),
                "instruction_count": len(instructions),
                "issue_count": len(issues),
                "has_errors": has_errors,
                "render_ready": not has_errors,
            },
        )

    def _get_or_create_input(
        self,
        inputs: list[TimelineInput],
        input_index: dict[str, str],
        local_path: str,
        input_type: str,
        asset_id: str | None,
        metadata: dict,
    ) -> str:
        normalized_path = str(Path(local_path))

        if normalized_path in input_index:
            return input_index[normalized_path]

        input_id = f"input_{len(inputs)}"

        inputs.append(
            TimelineInput(
                input_id=input_id,
                input_type=input_type,
                local_path=normalized_path,
                asset_id=asset_id,
                metadata=metadata,
            )
        )

        input_index[normalized_path] = input_id

        return input_id

    def _compile_effects(
        self,
        timeline: FinalTimeline,
    ) -> list[TimelineInstruction]:
        instructions: list[TimelineInstruction] = []

        for effect in timeline.effects:
            instructions.append(
                TimelineInstruction(
                    instruction_id=(
                        f"effect_instruction_{effect.effect_id}"
                    ),
                    instruction_type="apply_effect",
                    track_type="effect",
                    start_time=effect.start_time,
                    end_time=effect.end_time,
                    layer=100,
                    target_id=effect.target_id,
                    parameters={
                        "effect_type": effect.effect_type,
                        **effect.parameters,
                    },
                    metadata={
                        **effect.metadata,
                        "source_effect_id": effect.effect_id,
                    },
                )
            )

        return instructions

    def _compile_transitions(
        self,
        timeline: FinalTimeline,
    ) -> list[TimelineInstruction]:
        instructions: list[TimelineInstruction] = []

        for transition in timeline.transitions:
            start_time = max(
                0.0,
                transition.at_time,
            )

            end_time = min(
                timeline.duration,
                start_time + transition.duration,
            )

            instructions.append(
                TimelineInstruction(
                    instruction_id=(
                        "transition_instruction_"
                        f"{transition.transition_id}"
                    ),
                    instruction_type="apply_transition",
                    track_type="transition",
                    start_time=start_time,
                    end_time=end_time,
                    layer=101,
                    target_id=transition.target_id,
                    parameters={
                        "transition_type": (
                            transition.transition_type
                        ),
                        "duration": transition.duration,
                        **transition.parameters,
                    },
                    metadata={
                        **transition.metadata,
                        "source_transition_id": (
                            transition.transition_id
                        ),
                    },
                )
            )

        return instructions

    def _validate_instructions(
        self,
        timeline: FinalTimeline,
        instructions: list[TimelineInstruction],
    ) -> list[TimelineCompilerIssue]:
        issues: list[TimelineCompilerIssue] = []

        known_targets = {
            clip.clip_id
            for track in timeline.tracks
            for clip in track.clips
        }

        for instruction in instructions:
            if instruction.start_time < 0:
                issues.append(
                    TimelineCompilerIssue(
                        level="error",
                        code="negative_start_time",
                        message=(
                            "Instruction start_time "
                            "cannot be negative."
                        ),
                        source_id=instruction.instruction_id,
                    )
                )

            if instruction.end_time <= instruction.start_time:
                issues.append(
                    TimelineCompilerIssue(
                        level="error",
                        code="invalid_time_range",
                        message=(
                            "Instruction end_time must be "
                            "greater than start_time."
                        ),
                        source_id=instruction.instruction_id,
                    )
                )

            if instruction.end_time > timeline.duration:
                issues.append(
                    TimelineCompilerIssue(
                        level="warning",
                        code="instruction_exceeds_duration",
                        message=(
                            "Instruction extends beyond "
                            "timeline duration."
                        ),
                        source_id=instruction.instruction_id,
                    )
                )

            if (
                instruction.instruction_type
                in {"apply_effect", "apply_transition"}
                and instruction.target_id
                not in known_targets
            ):
                issues.append(
                    TimelineCompilerIssue(
                        level="error",
                        code="missing_target",
                        message=(
                            "Effect or transition target "
                            "does not exist."
                        ),
                        source_id=instruction.instruction_id,
                        metadata={
                            "target_id": instruction.target_id,
                        },
                    )
                )

        return issues

    def _requires_media_input(
        self,
        track_type: str,
    ) -> bool:
        return track_type in {
            "video_primary",
            "broll",
            "music",
            "sfx",
        }

    def _input_type(
        self,
        track_type: str,
    ) -> str:
        if track_type in {
            "video_primary",
            "broll",
        }:
            return "video"

        return "audio"

    def _instruction_type(
        self,
        track_type: str,
    ) -> str:
        mapping = {
            "video_primary": "place_video",
            "broll": "place_video_overlay",
            "music": "place_audio",
            "sfx": "place_audio",
            "subtitle": "draw_subtitle",
        }

        return mapping.get(
            track_type,
            "place_timeline_item",
        )

    def _sort_instructions(
        self,
        instructions: list[TimelineInstruction],
    ) -> list[TimelineInstruction]:
        return sorted(
            instructions,
            key=lambda item: (
                item.start_time,
                item.layer,
                item.instruction_type,
                item.instruction_id,
            ),
        )