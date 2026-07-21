from __future__ import annotations

from app.review.editing.ripple.runtime import RippleEditRuntime
from app.review.editing.state.store import TimelineRuntimeStore


def build_ripple_edit_runtime(*, store: TimelineRuntimeStore) -> RippleEditRuntime:
    return RippleEditRuntime(store=store)
