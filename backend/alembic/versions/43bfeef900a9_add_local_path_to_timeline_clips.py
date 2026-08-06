"""add local_path to timeline_clips

Revision ID: 43bfeef900a9
Revises: 2f95527a8dcd
Create Date: 2026-08-06 14:50:07.437792

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '43bfeef900a9'
down_revision: Union[str, Sequence[str], None] = '2f95527a8dcd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "timeline_clips",
        sa.Column("local_path", sa.String(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("timeline_clips", "local_path")
