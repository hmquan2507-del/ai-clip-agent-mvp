"""add runtime artifacts table

Revision ID: 49f8fc7693d8
Revises: dabff647fbf1
Create Date: 2026-07-06 16:01:59.798655

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '49f8fc7693d8'
down_revision: Union[str, Sequence[str], None] = 'dabff647fbf1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "runtime_artifacts",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("production_id", sa.String(), nullable=False),
        sa.Column("artifact_key", sa.String(), nullable=False),
        sa.Column("artifact_version", sa.Integer(), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("checksum", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_runtime_artifacts_production_id",
        "runtime_artifacts",
        ["production_id"],
    )

    op.create_index(
        "ix_runtime_artifacts_artifact_key",
        "runtime_artifacts",
        ["artifact_key"],
    )
    # ### end Alembic commands ###

def downgrade() -> None:
    op.drop_index("ix_runtime_artifacts_artifact_key", table_name="runtime_artifacts")
    op.drop_index("ix_runtime_artifacts_production_id", table_name="runtime_artifacts")
    op.drop_table("runtime_artifacts")
    # ### end Alembic commands ###
