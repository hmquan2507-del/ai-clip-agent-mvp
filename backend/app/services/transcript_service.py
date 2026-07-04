from app.repositories.transcript_repository import TranscriptRepository
from app.speech.factory import get_speech_provider


class TranscriptService:
    def __init__(self, db):
        self.repository = TranscriptRepository(db)
        self.speech_provider = get_speech_provider()

    def transcribe_production(self, job):
        source_asset = self.repository.get_source_video_asset(job.production_id)

        if source_asset is None:
            raise ValueError("Source video asset not found for production.")

        result = self.speech_provider.transcribe(
            file_path=source_asset.storage_path,
        )

        return self.repository.save_transcript_result(
            job=job,
            transcript_text=result.text,
            provider=result.provider,
            language=result.language,
            duration=result.duration,
        )