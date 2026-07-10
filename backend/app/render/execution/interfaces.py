from __future__ import annotations

from abc import ABC, abstractmethod

from app.render.execution.context import RenderContext
from app.render.execution.models import (
    RenderArtifact,
    RenderExecutionPlan,
    RenderGraph,
    RenderNode,
    RenderNodeExecutionResult,
    RenderResult,
)


class BaseRenderGraphBuilder(ABC):
    @abstractmethod
    def build(
        self,
        context: RenderContext,
    ) -> RenderGraph:
        raise NotImplementedError


class BaseRenderScheduler(ABC):
    @abstractmethod
    def schedule(
        self,
        graph: RenderGraph,
    ) -> RenderExecutionPlan:
        raise NotImplementedError


class BaseRenderExecutor(ABC):
    @abstractmethod
    def execute(
        self,
        context: RenderContext,
    ) -> RenderResult:
        raise NotImplementedError


class BaseRenderNodeExecutor(ABC):
    @abstractmethod
    def supports(
        self,
        node: RenderNode,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    def execute(
        self,
        context: RenderContext,
        node: RenderNode,
    ) -> RenderNodeExecutionResult:
        raise NotImplementedError


class BaseArtifactWriter(ABC):
    @abstractmethod
    def write(
        self,
        context: RenderContext,
        artifact: RenderArtifact,
    ) -> RenderArtifact:
        raise NotImplementedError


class BaseProgressReporter(ABC):
    @abstractmethod
    def report(
        self,
        context: RenderContext,
        message: str,
    ) -> None:
        raise NotImplementedError