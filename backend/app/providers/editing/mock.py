from __future__ import annotations

from app.providers.editing.base import BaseEditingProvider


class MockEditingProvider(BaseEditingProvider):
    async def generate_editing_plan(
        self,
        production_id: str,
        transcript: str,
        target_duration_seconds: int | None = None,
    ) -> dict:
        return {
            "summary": "Mock editing plan generated successfully.",
            "segments": [
                {
                    "start_time": 0,
                    "end_time": 5,
                    "action": "hook",
                    "reason": "Strong opening segment.",
                    "priority": 10,
                    "metadata": {
                        "note": "Use as video hook"
                    },
                },
                {
                    "start_time": 5,
                    "end_time": 20,
                    "action": "keep",
                    "reason": "Main content is useful.",
                    "priority": 8,
                    "metadata": {},
                },
                {
                    "start_time": 20,
                    "end_time": 25,
                    "action": "cut",
                    "reason": "Low-value filler content.",
                    "priority": 3,
                    "metadata": {},
                },
                {
                    "start_time": 25,
                    "end_time": 35,
                    "action": "broll",
                    "reason": "Good place to add visual support.",
                    "priority": 7,
                    "metadata": {
                        "suggestion": "Add relevant product or workflow screen"
                    },
                },
            ],
        }