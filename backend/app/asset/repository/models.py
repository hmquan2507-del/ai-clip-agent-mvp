from sqlalchemy import JSON, String
from sqlalchemy.orm import mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class AssetModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "assets"

    provider_key = mapped_column(String, nullable=False, index=True)
    provider_asset_id = mapped_column(String, nullable=False, index=True)
    asset_type = mapped_column(String, nullable=False, index=True)
    title = mapped_column(String)
    description = mapped_column(String)
    metadata_json = mapped_column(JSON)
    status = mapped_column(String, nullable=False, index=True)
    checksum = mapped_column(String)
    local_path = mapped_column(String)
    remote_url = mapped_column(String, index=True)
    thumbnail_url = mapped_column(String)
    preview_url = mapped_column(String)
    license = mapped_column(String)
