from __future__ import annotations

import uuid

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RuntimeArtifact(Base):
    __tablename__ = "runtime_artifacts"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    production_id: Mapped[str] = mapped_column(
        String,
        index=True,
        nullable=False,
    )

    artifact_key: Mapped[str] = mapped_column(
        String,
        index=True,
        nullable=False,
    )

    artifact_version: Mapped[int] = mapped_column(
        default=1,
        nullable=False,
    )

    payload_json: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    checksum: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )