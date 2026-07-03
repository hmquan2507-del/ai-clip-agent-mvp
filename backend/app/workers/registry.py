from app.db.enums import QueueType
from app.workers.base import BaseWorker
from app.workers.broll_worker import BrollWorker
from app.workers.music_worker import MusicWorker
from app.workers.render_worker import RenderWorker
from app.workers.subtitle_worker import SubtitleWorker
from app.workers.transcript_worker import TranscriptWorker


class WorkerRegistry:
    def __init__(self):
        self._workers: dict[QueueType, BaseWorker] = {
            QueueType.TRANSCRIPT: TranscriptWorker(),
            QueueType.SUBTITLE: SubtitleWorker(),
            QueueType.BROLL: BrollWorker(),
            QueueType.MUSIC: MusicWorker(),
            QueueType.RENDER: RenderWorker(),
        }

    def get_worker(self, queue_type: QueueType) -> BaseWorker:
        worker = self._workers.get(queue_type)

        if worker is None:
            raise ValueError(f"No worker registered for queue type: {queue_type}")

        return worker