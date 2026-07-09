from __future__ import annotations

from app.timeline.semantic.runtime import TimelineSemanticEngine


def build_timeline_semantic_engine() -> TimelineSemanticEngine:
    return TimelineSemanticEngine()