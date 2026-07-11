"""add production assets table

Revision ID: 3b99727d5d05
Revises: ba4244963bdb
Create Date: 2026-07-11 17:00:58.755760
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "3b99727d5d05"
down_revision: Union[str, Sequence[str], None] = "ba4244963bdb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "production_assets",
        sa.Column(
            "production_id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "type",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "filename",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "mime_type",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "size_bytes",
            sa.BigInteger(),
            nullable=True,
        ),
        sa.Column(
            "storage_path",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "deleted_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.Column(
            "version",
            sa.Integer(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["production_id"],
            ["productions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f(
            "ix_production_assets_production_id"
        ),
        "production_assets",
        ["production_id"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_production_assets_type"
        ),
        "production_assets",
        ["type"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f(
            "ix_production_assets_type"
        ),
        table_name="production_assets",
    )

    op.drop_index(
        op.f(
            "ix_production_assets_production_id"
        ),
        table_name="production_assets",
    )

    op.drop_table(
        "production_assets"
    )