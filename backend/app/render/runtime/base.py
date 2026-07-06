from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.render.runtime.models import RenderContext, RenderRuntimeResult


class BaseRenderRuntime(ABC):
    runtime_name: str = "base_render_runtime"

    @abstractmethod
    def run(
        self,
        context: RenderContext,
        **kwargs: Any,
    ) -> RenderRuntimeResult:
        raise NotImplementedError