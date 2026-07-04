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
from app.workers.subtitle_worker import SubtitleWorker
from app.workers.broll_runtime_worker import BrollRuntimeWorker
from app.workers.sound_effect_runtime_worker import SoundEffectRuntimeWorker
from app.workers.music_runtime_worker import MusicRuntimeWorker
from app.workers.render_runtime_worker import RenderRuntimeWorker

class WorkerRegistry:
    def __init__(self, db: Session | None = None):
        self._workers: dict[QueueType, BaseWorker] = {
            QueueType.TRANSCRIPT: TranscriptWorker(db=db),
            QueueType.AI_EDITING: EditingWorker(db=db),
            QueueType.SUBTITLE_RUNTIME: SubtitleWorker(db=db),
            QueueType.BROLL_RUNTIME: BrollRuntimeWorker(db=db),
            QueueType.SOUND_EFFECT_RUNTIME: SoundEffectRuntimeWorker(db=db),
            QueueType.MUSIC_RUNTIME: MusicRuntimeWorker(db=db),
            QueueType.RENDER_RUNTIME: RenderRuntimeWorker(db=db),
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