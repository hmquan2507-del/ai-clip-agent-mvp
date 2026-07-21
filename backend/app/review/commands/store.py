from __future__ import annotations

from collections import deque
from threading import RLock

from app.review.commands.models import (
    AICommandSubmission,
)


class AICommandSubmissionStore:
    def __init__(self, *, maximum_size: int = 1000):
        if maximum_size < 1:
            raise ValueError("maximum_size must be positive.")
        self.maximum_size = int(maximum_size)
        self._lock = RLock()
        self._items: dict[str, AICommandSubmission] = {}
        self._order: deque[str] = deque()
        self._request_ids: dict[
            tuple[str, str, str], str
        ] = {}

    def add(
        self,
        submission: AICommandSubmission,
    ) -> tuple[AICommandSubmission, bool]:
        with self._lock:
            request_key = self._request_key(submission)
            if request_key is not None:
                existing_id = self._request_ids.get(request_key)
                if existing_id is not None:
                    return self._items[existing_id].clone(), True

            clone = submission.clone()
            self._items[clone.submission_id] = clone
            self._order.append(clone.submission_id)
            if request_key is not None:
                self._request_ids[request_key] = clone.submission_id
            self._trim()
            return clone.clone(), False

    @property
    def count(self) -> int:
        with self._lock:
            return len(self._items)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()
            self._order.clear()
            self._request_ids.clear()

    def _trim(self) -> None:
        while len(self._order) > self.maximum_size:
            submission_id = self._order.popleft()
            removed = self._items.pop(submission_id, None)
            if removed is None:
                continue
            request_key = self._request_key(removed)
            if request_key is not None:
                self._request_ids.pop(request_key, None)

    @staticmethod
    def _request_key(
        submission: AICommandSubmission,
    ) -> tuple[str, str, str] | None:
        if not submission.client_request_id:
            return None
        return (
            submission.production_id,
            submission.session_id,
            submission.client_request_id,
        )
