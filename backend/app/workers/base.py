from abc import ABC, abstractmethod

from app.db.models.queue_job import QueueJob


class BaseWorker(ABC):
    @abstractmethod
    def run(self, job: QueueJob) -> dict:
        """Run a queue job and return a structured result."""
        raise NotImplementedError