from __future__ import annotations

from abc import ABC, abstractmethod

from app.review.application.suggestion_models import (
    ReviewAISuggestionApplicationResult,
)
from app.review.suggestions.lifecycle_models import (
    AISuggestionLifecycleSnapshot,
)
from app.review.suggestions.models import AISuggestionReadModel


class AISuggestionRegeneratorInterface(ABC):
    @abstractmethod
    def regenerate(
        self,
        *,
        production_id: str,
        session_id: str,
        timeline_revision: int,
        current: AISuggestionLifecycleSnapshot,
    ) -> AISuggestionReadModel:
        raise NotImplementedError


class ReviewAISuggestionApplicationServiceInterface(ABC):
    @abstractmethod
    def get_ai_suggestions(
        self,
        production_id: str,
        *,
        session_id: str,
    ) -> ReviewAISuggestionApplicationResult:
        raise NotImplementedError

    @abstractmethod
    def select_ai_suggestion(
        self,
        production_id: str,
        *,
        session_id: str,
        suggestion_id: str | None,
        expected_lifecycle_revision: int | None = None,
    ) -> ReviewAISuggestionApplicationResult:
        raise NotImplementedError

    @abstractmethod
    def apply_ai_suggestion(
        self,
        production_id: str,
        *,
        session_id: str,
        suggestion_id: str,
        expected_timeline_revision: int | None = None,
        expected_lifecycle_revision: int | None = None,
    ) -> ReviewAISuggestionApplicationResult:
        raise NotImplementedError

    @abstractmethod
    def dismiss_ai_suggestion(
        self,
        production_id: str,
        *,
        session_id: str,
        suggestion_id: str,
        expected_lifecycle_revision: int | None = None,
    ) -> ReviewAISuggestionApplicationResult:
        raise NotImplementedError

    @abstractmethod
    def regenerate_ai_suggestions(
        self,
        production_id: str,
        *,
        session_id: str,
        expected_lifecycle_revision: int | None = None,
    ) -> ReviewAISuggestionApplicationResult:
        raise NotImplementedError
