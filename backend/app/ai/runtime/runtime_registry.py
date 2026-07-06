from __future__ import annotations

from app.ai.decision.decision_engine import DecisionEngine
from app.ai.emotion.emotion_engine import EmotionEngine
from app.ai.hook.hook_detection_engine import HookDetectionEngine
from app.ai.runtime.engine_registry import EngineRegistry
from app.ai.story.story_engine import StoryEngine
from app.ai.style.editing_style_engine import EditingStyleEngine
from app.ai.execution.execution_planner import EditingExecutionPlanner

def build_default_engine_registry() -> EngineRegistry:
    registry = EngineRegistry()

    registry.register("hook_detection", HookDetectionEngine())
    registry.register("story_engine", StoryEngine())
    registry.register("emotion_engine", EmotionEngine())
    registry.register("editing_style_engine", EditingStyleEngine())
    registry.register("decision_engine", DecisionEngine())
    registry.register("editing_execution_planner", EditingExecutionPlanner())

    return registry