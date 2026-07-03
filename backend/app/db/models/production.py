from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity
from app.db.enums import ProductionStatus


class Production(BaseEntity):
    __tablename__ = "productions"

    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"))

    title: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[ProductionStatus] = mapped_column(
        Enum(ProductionStatus),
        default=ProductionStatus.DRAFT,
        index=True,
    )
    style: Mapped[str | None] = mapped_column(String, nullable=True)

    progress: Mapped[int] = mapped_column(Integer, default=0)

    workspace = relationship("Workspace", back_populates="productions")
    assets = relationship("Asset", back_populates="production")
    clips = relationship("Clip", back_populates="production")
    render_jobs = relationship("RenderJob", back_populates="production")
    exports = relationship("Export", back_populates="production")
    queue_jobs = relationship("QueueJob", back_populates="production")