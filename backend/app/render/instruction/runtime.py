from __future__ import annotations

from typing import Any

from app.render.instruction.builder import RenderInstructionBuilder
from app.render.instruction.models import RenderInstructionSet


class RenderInstructionRuntime:
    runtime_name = "render_instruction_runtime"

    def __init__(self):
        self.builder = RenderInstructionBuilder()

    def run(
        self,
        production_id: str,
        composition: dict[str, Any],
    ) -> RenderInstructionSet:
        return self.builder.build(
            production_id=production_id,
            composition=composition,
        )