from __future__ import annotations

from app.ai.structured_output.models import StructuredOutputResult
from app.ai.structured_output.parser import StructuredOutputParser
from app.ai.structured_output.validator import StructuredOutputValidator


class StructuredOutputRuntime:
    def __init__(self):
        self.parser = StructuredOutputParser()
        self.validator = StructuredOutputValidator()

    def parse_and_validate(
        self,
        raw_text: str,
        required_keys: list[str] | None = None,
    ) -> StructuredOutputResult:
        data = self.parser.parse_json(raw_text)
        errors = self.validator.validate(
            data=data,
            required_keys=required_keys,
        )

        return StructuredOutputResult(
            data=data,
            is_valid=len(errors) == 0,
            errors=errors,
            raw_text=raw_text,
        )