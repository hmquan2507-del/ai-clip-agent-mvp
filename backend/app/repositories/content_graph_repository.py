from __future__ import annotations

from sqlalchemy.orm import Session, selectinload

from app.db.enums import ContentEmotion, ContentGraphStatus, ContentSegmentType
from app.db.models.content_graph import ContentGraph, ContentSegment


class ContentGraphRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_graph(
        self,
        production_id: str,
        language: str | None = None,
        summary: str | None = None,
        topic_json: str | None = None,
        speaker_json: str | None = None,
        metadata_json: str | None = None,
    ) -> ContentGraph:
        graph = ContentGraph(
            production_id=production_id,
            status=ContentGraphStatus.PROCESSING,
            language=language,
            summary=summary,
            topic_json=topic_json,
            speaker_json=speaker_json,
            metadata_json=metadata_json,
        )

        self.db.add(graph)
        self.db.commit()
        self.db.refresh(graph)

        return graph

    def get_by_id(self, graph_id: str) -> ContentGraph | None:
        return (
            self.db.query(ContentGraph)
            .options(selectinload(ContentGraph.segments))
            .filter(ContentGraph.id == graph_id)
            .first()
        )

    def get_latest_by_production(self, production_id: str) -> ContentGraph | None:
        return (
            self.db.query(ContentGraph)
            .options(selectinload(ContentGraph.segments))
            .filter(ContentGraph.production_id == production_id)
            .order_by(ContentGraph.created_at.desc())
            .first()
        )

    def add_segment(
        self,
        content_graph_id: str,
        start_time: float,
        end_time: float,
        text: str,
        segment_type: ContentSegmentType = ContentSegmentType.UNKNOWN,
        emotion: ContentEmotion = ContentEmotion.NEUTRAL,
        topic: str | None = None,
        importance_score: float = 0,
        viral_potential_score: float = 0,
        speaker_id: str | None = None,
        order_index: int = 0,
        metadata_json: str | None = None,
    ) -> ContentSegment:
        segment = ContentSegment(
            content_graph_id=content_graph_id,
            start_time=start_time,
            end_time=end_time,
            text=text,
            type=segment_type,
            emotion=emotion,
            topic=topic,
            importance_score=importance_score,
            viral_potential_score=viral_potential_score,
            speaker_id=speaker_id,
            order_index=order_index,
            metadata_json=metadata_json,
        )

        self.db.add(segment)
        self.db.commit()
        self.db.refresh(segment)

        return segment

    def update_metadata_json(
        self,
        graph_id: str,
        metadata_json: str,
    ) -> ContentGraph:
        graph = self.get_by_id(graph_id)

        if graph is None:
            raise ValueError("Content graph not found")

        graph.metadata_json = metadata_json

        self.db.add(graph)
        self.db.commit()
        self.db.refresh(graph)

        return graph

    def mark_completed(
        self,
        graph_id: str,
        summary: str | None = None,
        topic_json: str | None = None,
        speaker_json: str | None = None,
        metadata_json: str | None = None,
    ) -> ContentGraph:
        graph = self.get_by_id(graph_id)

        if graph is None:
            raise ValueError("Content graph not found")

        graph.status = ContentGraphStatus.COMPLETED
        graph.summary = summary
        graph.topic_json = topic_json
        graph.speaker_json = speaker_json
        graph.metadata_json = metadata_json

        self.db.commit()
        self.db.refresh(graph)

        return graph

    def mark_failed(
        self,
        graph_id: str,
        error_message: str,
    ) -> ContentGraph:
        graph = self.get_by_id(graph_id)

        if graph is None:
            raise ValueError("Content graph not found")

        graph.status = ContentGraphStatus.FAILED
        graph.metadata_json = error_message

        self.db.commit()
        self.db.refresh(graph)

        return graph

    def delete_by_production(self, production_id: str) -> bool:
        graph = self.get_latest_by_production(production_id)

        if graph is None:
            return False

        self.db.delete(graph)
        self.db.commit()

        return True