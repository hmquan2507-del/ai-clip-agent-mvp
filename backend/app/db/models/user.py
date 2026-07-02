from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity


class User(BaseEntity):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)

    workspaces = relationship("Workspace", back_populates="owner")