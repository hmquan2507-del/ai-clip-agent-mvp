from __future__ import annotations

from app.timeline.camera_movement.runtime import CameraMovementRuntime


def build_camera_movement_runtime() -> CameraMovementRuntime:
    return CameraMovementRuntime()