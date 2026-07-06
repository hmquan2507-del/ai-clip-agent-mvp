from __future__ import annotations

import json
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.content_graph_repository import ContentGraphRepository
from app.repositories.production_repository import ProductionRepository
from app.repositories.queue_repository import QueueRepository
from app.services.content_understanding_engine import ContentUnderstandingEngine


class ContentUnderstandingService:
    def __init__(self, db: Session):
        self.db = db

        self.production_repo = ProductionRepository(db)
        self.queue_repo = QueueRepository(db)
        self.content_graph_repo = ContentGraphRepository(db)
        self.engine = ContentUnderstandingEngine()

    def generate_content_graph(
        self,
        production_id: UUID,
        language: str | None = "vi",
    ):
        production = self.production_repo.get_by_id(production_id)

        if production is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Production not found",
            )

        transcript_text = self._get_latest_transcript_text(production_id)

        graph = self.content_graph_repo.create_graph(
            production_id=str(production_id),
            language=language,
        )

        try:
            result = self.engine.build_from_transcript(
                transcript_text=transcript_text,
                language=language,
            )

            for segment in result["segments"]:
                self.content_graph_repo.add_segment(
                    content_graph_id=graph.id,
                    start_time=segment["start_time"],
                    end_time=segment["end_time"],
                    text=segment["text"],
                    segment_type=segment["type"],
                    emotion=segment["emotion"],
                    topic=segment["topic"],
                    importance_score=segment["importance_score"],
                    viral_potential_score=segment["viral_potential_score"],
                    speaker_id=segment["speaker_id"],
                    order_index=segment["order_index"],
                    metadata_json=segment["metadata_json"],
                )

            return self.content_graph_repo.mark_completed(
                graph_id=graph.id,
                summary=result["summary"],
                topic_json=self.engine.dumps_json(result["topics"]),
                speaker_json=self.engine.dumps_json(result["speakers"]),
                metadata_json=self.engine.dumps_json(result["metadata"]),
            )

        except Exception as exc:
            self.content_graph_repo.mark_failed(
                graph_id=graph.id,
                error_message=str(exc),
            )
            raise

    def get_latest_content_graph(self, production_id: UUID):
        graph = self.content_graph_repo.get_latest_by_production(
            production_id=str(production_id),
        )

        if graph is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content graph not found",
            )

        return graph

    def delete_latest_content_graph(self, production_id: UUID) -> bool:
        deleted = self.content_graph_repo.delete_by_production(
            production_id=str(production_id),
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content graph not found",
            )

        return True

    def _get_latest_transcript_text(self, production_id: UUID,) -> str:
        job = self.queue_repo.get_latest_completed_transcript(
            production_id=production_id,
        )

        if job is None or not job.result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Completed transcript result not found",
            )

        try:
            result = json.loads(job.result)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Invalid transcript result format: {exc}",
            ) from exc

        transcript_text = result.get("text")

        if not transcript_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transcript text is empty",
            )

        return transcript_text