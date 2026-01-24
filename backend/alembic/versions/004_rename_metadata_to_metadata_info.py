"""Rename reserved 'metadata' columns to 'metadata_info'

Revision ID: 004_rename_metadata
Revises: 003_add_video_distributions
Create Date: 2026-01-23

The attribute name 'metadata' is reserved in SQLAlchemy's Declarative API (conflicts with
Base.metadata). This migration renames the columns in music and publication_schedules
to 'metadata_info' so the ORM models can use a non-reserved attribute name.
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "004_rename_metadata"
down_revision = "003_add_video_distributions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # music.metadata -> metadata_info
    op.alter_column(
        "music",
        "metadata",
        new_column_name="metadata_info",
    )
    # publication_schedules.metadata -> metadata_info
    op.alter_column(
        "publication_schedules",
        "metadata",
        new_column_name="metadata_info",
    )


def downgrade() -> None:
    op.alter_column(
        "music",
        "metadata_info",
        new_column_name="metadata",
    )
    op.alter_column(
        "publication_schedules",
        "metadata_info",
        new_column_name="metadata",
    )
