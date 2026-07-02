from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity


class Workspace(BaseEntity):
    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(String)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"))

    owner = relationship("User", back_populates="workspaces")
    productions = relationship("Production", back_populates="workspace")