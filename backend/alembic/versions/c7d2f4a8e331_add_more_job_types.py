"""add rotate/extract/crop/replace/remove-watermark/bookmarks job types

Revision ID: c7d2f4a8e331
Revises: b3c9a1e5f210
Create Date: 2026-07-26 00:00:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'c7d2f4a8e331'
down_revision = 'b3c9a1e5f210'
branch_labels = None
depends_on = None

NEW_VALUES = ["ROTATE", "EXTRACT", "CROP", "REPLACE_PAGES", "REMOVE_WATERMARK", "BOOKMARKS"]


def upgrade() -> None:
    for value in NEW_VALUES:
        op.execute(f"ALTER TYPE job_type ADD VALUE IF NOT EXISTS '{value}'")


def downgrade() -> None:
    # Postgres does not support removing enum values.
    pass
