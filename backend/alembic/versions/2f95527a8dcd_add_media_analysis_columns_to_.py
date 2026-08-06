"""add media analysis columns to production_assets

Revision ID: 2f95527a8dcd
Revises: 3b99727d5d05
Create Date: 2026-08-05 10:11:48.387722

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2f95527a8dcd'
down_revision: Union[str, Sequence[str], None] = '3b99727d5d05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Autogenerate also picked up a large amount of pre-existing,
    # unrelated schema drift (the "assets" table shape vs. the current
    # AssetModel, GUID type coercion on production_assets.id/
    # production_id, queue_jobs.type enum) - trimmed to only the columns
    # this migration is actually about.
    op.add_column('production_assets', sa.Column('duration', sa.Float(), nullable=True))
    op.add_column('production_assets', sa.Column('width', sa.Integer(), nullable=True))
    op.add_column('production_assets', sa.Column('height', sa.Integer(), nullable=True))
    op.add_column('production_assets', sa.Column('fps', sa.Float(), nullable=True))
    op.add_column('production_assets', sa.Column('video_codec', sa.String(), nullable=True))
    op.add_column('production_assets', sa.Column('audio_codec', sa.String(), nullable=True))
    op.add_column('production_assets', sa.Column('has_audio', sa.Boolean(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('production_assets', 'has_audio')
    op.drop_column('production_assets', 'audio_codec')
    op.drop_column('production_assets', 'video_codec')
    op.drop_column('production_assets', 'fps')
    op.drop_column('production_assets', 'height')
    op.drop_column('production_assets', 'width')
    op.drop_column('production_assets', 'duration')
