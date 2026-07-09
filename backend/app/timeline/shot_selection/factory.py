from __future__ import annotations

from app.timeline.shot_selection.runtime import ShotSelectionRuntime


def build_shot_selection_runtime() -> ShotSelectionRuntime:
    return ShotSelectionRuntime()