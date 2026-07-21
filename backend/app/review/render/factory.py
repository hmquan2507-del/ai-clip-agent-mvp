from app.review.editing.state.store import TimelineRuntimeStore
from app.review.render.runtime import ReviewToRenderHandoffRuntime


def build_review_to_render_handoff_runtime(store: TimelineRuntimeStore) -> ReviewToRenderHandoffRuntime:
    return ReviewToRenderHandoffRuntime(store)
