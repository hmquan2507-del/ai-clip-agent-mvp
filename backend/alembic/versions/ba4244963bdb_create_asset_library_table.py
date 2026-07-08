"""create asset library table

Revision ID: ba4244963bdb
Revises: 49f8fc7693d8
Create Date: 2026-07-08 16:06:41.476187

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ba4244963bdb'
down_revision: Union[str, Sequence[str], None] = '49f8fc7693d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "asset_library",
        sa.Column("provider_key", sa.String(), nullable=False),
        sa.Column("provider_asset_id", sa.String(), nullable=True),
        sa.Column("asset_type", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("tags_json", sa.Text(), nullable=True),
        sa.Column("keywords_json", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("local_path", sa.String(), nullable=True),
        sa.Column("remote_url", sa.Text(), nullable=True),
        sa.Column("thumbnail_url", sa.Text(), nullable=True),
        sa.Column("preview_url", sa.Text(), nullable=True),
        sa.Column("checksum", sa.String(), nullable=True),
        sa.Column("duration", sa.Float(), nullable=True),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("fps", sa.Float(), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("license", sa.String(), nullable=True),
        sa.Column("language", sa.String(), nullable=True),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_asset_library_provider_key", "asset_library", ["provider_key"])
    op.create_index("ix_asset_library_provider_asset_id", "asset_library", ["provider_asset_id"])
    op.create_index("ix_asset_library_asset_type", "asset_library", ["asset_type"])
    op.create_index("ix_asset_library_status", "asset_library", ["status"])
    op.create_index("ix_asset_library_checksum", "asset_library", ["checksum"])


def downgrade() -> None:
    op.drop_table("asset_library")