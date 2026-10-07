"""add page ops / signature / html-epub job types

Revision ID: b3c9a1e5f210
Revises: fa701903ec9f
Create Date: 2026-07-26 00:00:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'b3c9a1e5f210'
down_revision = 'fa701903ec9f'
branch_labels = None
depends_on = None

NEW_VALUES = [
    "FORM_FILL",
    "DELETE_PAGES",
    "INSERT_BLANK_PAGE",
    "DUPLICATE_PAGE",
    "REORDER_PAGES",
    "PAGE_NUMBERS",
    "HEADER_FOOTER",
    "SIGN",
    "PDF_TO_HTML",
    "PDF_TO_EPUB",
    "PERMISSIONS",
]


def upgrade() -> None:
    # Postgres requires ADD VALUE to run outside a transaction block per
    # value in older versions; each statement is run separately and,
    # unlike a table alter, cannot be wrapped in the surrounding
    # migration transaction on PG < 12. Neon runs a modern PG version
    # where this works within `alembic upgrade`'s default autocommit-off
    # connection, so IF NOT EXISTS guards re-runs safely either way.
    for value in NEW_VALUES:
        op.execute(f"ALTER TYPE job_type ADD VALUE IF NOT EXISTS '{value}'")


def downgrade() -> None:
    # Postgres does not support removing enum values; downgrading this
    # migration is a no-op by design (matches how enum-only migrations
    # are handled elsewhere in this project).
    pass
