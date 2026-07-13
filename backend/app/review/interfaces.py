from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from app.product.adapters import ProductWorkspaceSnapshot
from app.review.models import ReviewWorkspace


class ReviewWorkspaceBuilderInterface(ABC):
    """
    Interface for building a ReviewWorkspace from a ProductWorkspaceSnapshot.
    """

    @abstractmethod
    def build_from_snapshot(
        self, snapshot: ProductWorkspaceSnapshot
    ) -> ReviewWorkspace:
        """
        Builds a ReviewWorkspace from a ProductWorkspaceSnapshot.
        """
        raise NotImplementedError


class ReviewWorkspaceServiceInterface(ABC):
    """
    Interface for managing the ReviewWorkspace.
    """

    @abstractmethod
    def build_workspace(self, production_id: str, **kwargs: Any) -> ReviewWorkspace:
        """
        Builds a new ReviewWorkspace for a given production.
        """
        raise NotImplementedError

    @abstractmethod
    def refresh(self, workspace: ReviewWorkspace, **kwargs: Any) -> ReviewWorkspace:
        """
        Refreshes the state of an existing ReviewWorkspace.
        """
        raise NotImplementedError

    @abstractmethod
    def save_state(self, workspace: ReviewWorkspace, **kwargs: Any) -> None:
        """
        Saves the current state of the ReviewWorkspace.
        """
        raise NotImplementedError

    @abstractmethod
    def reset(self, workspace: ReviewWorkspace, **kwargs: Any) -> ReviewWorkspace:
        """
        Resets the ReviewWorkspace to its initial state.
        """
        raise NotImplementedError
