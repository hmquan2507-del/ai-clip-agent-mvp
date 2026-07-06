from __future__ import annotations

from typing import Any

from app.render.instruction.models import RenderInstruction, RenderInstructionSet
from app.render.instruction.rules import (
    default_outputs,
    instruction_type_from_layer,
    render_operation_from_instruction,
)


class RenderInstructionBuilder:
    def build(
        self,
        production_id: str,
        composition: dict[str, Any],
    ) -> RenderInstructionSet:
        instructions: list[RenderInstruction] = []

        instructions.append(
            RenderInstruction(
                instruction_id="instruction_0",
                instruction_type="decode",
                operation="decode_source_video",
                inputs={"source": "source_video"},
                outputs={"target": "decoded_video_stream"},
                priority="high",
                metadata={"system_instruction": True},
            )
        )

        layers = composition.get("layers", [])
        if not isinstance(layers, list):
            layers = []

        for layer in layers:
            if not isinstance(layer, dict):
                continue

            instructions.extend(
                self._build_layer_instructions(
                    layer=layer,
                    start_index=len(instructions),
                )
            )

        instructions.append(
            RenderInstruction(
                instruction_id=f"instruction_{len(instructions)}",
                instruction_type="encode",
                operation="encode_output",
                inputs={"source": "composited_timeline"},
                outputs={"target": "final_video"},
                parameters={
                    "format": "mp4",
                    "codec": "h264",
                    "audio_codec": "aac",
                },
                priority="high",
                metadata={"system_instruction": True},
            )
        )

        return RenderInstructionSet(
            production_id=production_id,
            instructions=instructions,
            metadata={
                "builder": "render_instruction_builder",
                "instruction_count": len(instructions),
                "has_decode_instruction": any(
                    item.operation == "decode_source_video"
                    for item in instructions
                ),
                "has_encode_instruction": any(
                    item.operation == "encode_output"
                    for item in instructions
                ),
            },
        )

    def _build_layer_instructions(
        self,
        layer: dict[str, Any],
        start_index: int,
    ) -> list[RenderInstruction]:
        instructions: list[RenderInstruction] = []

        layer_key = str(layer.get("layer_key") or "unknown_layer")
        layer_type = str(layer.get("layer_type") or "unknown")
        track_key = str(layer.get("track_key") or "unknown")

        events = layer.get("events", [])
        if not isinstance(events, list):
            return instructions

        for event in events:
            if not isinstance(event, dict):
                continue

            raw_operation = str(event.get("operation") or "")
            instruction_type = instruction_type_from_layer(
                layer_type=layer_type,
                operation=raw_operation,
            )

            operation = render_operation_from_instruction(
                instruction_type=instruction_type,
                raw_operation=raw_operation,
            )

            instructions.append(
                RenderInstruction(
                    instruction_id=f"instruction_{start_index + len(instructions)}",
                    instruction_type=instruction_type,
                    operation=operation,
                    layer_key=layer_key,
                    layer_type=layer_type,
                    track_key=track_key,
                    start_time=self._safe_float_or_none(event.get("start_time")),
                    end_time=self._safe_float_or_none(event.get("end_time")),
                    parameters=event.get("parameters")
                    if isinstance(event.get("parameters"), dict)
                    else {},
                    inputs={
                        "layer_key": layer_key,
                        "track_key": track_key,
                        "event": event,
                    },
                    outputs=default_outputs(
                        layer_key=layer_key,
                        instruction_type=instruction_type,
                    ),
                    priority=str(event.get("priority") or "medium"),
                    metadata={
                        "source_event": event,
                    },
                )
            )

        return instructions

    def _safe_float_or_none(self, value: Any) -> float | None:
        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None