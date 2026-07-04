from sqlalchemy.orm import Session

from app.db.enums import QueueType
from app.workers.base import BaseWorker
from app.workers.broll_worker import BrollWorker
from app.workers.music_worker import MusicWorker
from app.workers.render_worker import RenderWorker
from app.workers.subtitle_worker import SubtitleWorker
from app.workers.transcript_worker import TranscriptWorker
from app.workers.editing_worker import EditingWorker
from app.workers.timeline_worker import TimelineWorker

class WorkerRegistry:
    def __init__(self, db: Session | None = None):
        self._workers: dict[QueueType, BaseWorker] = {
            QueueType.TRANSCRIPT: TranscriptWorker(db=db),
            QueueType.AI_EDITING: EditingWorker(db=db),
            QueueType.SUBTITLE: SubtitleWorker(),
            QueueType.BROLL: BrollWorker(),
            QueueType.MUSIC: MusicWorker(),
            QueueType.RENDER: RenderWorker(),
            QueueType.TIMELINE: TimelineWorker(db=db),
        }

    def get_worker(self, queue_type: QueueType) -> BaseWorker:
        worker = self._workers.get(queue_type)

        if worker is None:
            raise ValueError(f"No worker registered for queue type: {queue_type}")

        return worker