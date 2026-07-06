from __future__ import annotations

from sqlalchemy import Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity
from app.db.enums import (
    ContentEmotion,
    ContentGraphStatus,
    ContentSegmentType,
)


class ContentGraph(BaseEntity):
    __tablename__ = "content_graphs"

    production_id: Mapped[str] = mapped_column(
        ForeignKey("productions.id"),
        index=True,
        nullable=False,
    )

    status: Mapped[ContentGraphStatus] = mapped_column(
        Enum(ContentGraphStatus),
        default=ContentGraphStatus.DRAFT,
        index=True,
        nullable=False,
    )

    language: Mapped[str | None] = mapped_column(String, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    topic_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    speaker_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    segments: Mapped[list["ContentSegment"]] = relationship(
        "ContentSegment",
        back_populates="content_graph",
        cascade="all, delete-orphan",
    )


class ContentSegment(BaseEntity):
    __tablename__ = "content_segments"

    content_graph_id: Mapped[str] = mapped_column(
        ForeignKey("content_graphs.id"),
        index=True,
        nullable=False,
    )

    start_time: Mapped[float] = mapped_column(Float, nullable=False)
    end_time: Mapped[float] = mapped_column(Float, nullable=False)

    type: Mapped[ContentSegmentType] = mapped_column(
        Enum(ContentSegmentType),
        default=ContentSegmentType.UNKNOWN,
        index=True,
        nullable=False,
    )

    emotion: Mapped[ContentEmotion] = mapped_column(
        Enum(ContentEmotion),
        default=ContentEmotion.NEUTRAL,
        index=True,
        nullable=False,
    )

    topic: Mapped[str | None] = mapped_column(String, nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    importance_score: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    viral_potential_score: Mapped[float] = mapped_column(Float, default=0, nullable=False)

    speaker_id: Mapped[str | None] = mapped_column(String, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    content_graph: Mapped["ContentGraph"] = relationship(
        "ContentGraph",
        back_populates="segments",
    )