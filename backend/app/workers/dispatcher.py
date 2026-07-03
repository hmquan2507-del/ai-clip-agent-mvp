from app.db.models.queue_job import QueueJob
from app.workers.registry import WorkerRegistry


class WorkerDispatcher:
    def __init__(self):
        self.registry = WorkerRegistry()

    def dispatch(self, job: QueueJob) -> dict:
        worker = self.registry.get_worker(job.type)
        return worker.run(job)