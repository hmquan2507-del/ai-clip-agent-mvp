from __future__ import annotations

from app.media.validation.runtime import MediaValidationRuntime


def build_media_validation_runtime() -> MediaValidationRuntime:
    return MediaValidationRuntime()