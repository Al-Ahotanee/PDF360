"""add public_shares table

Revision ID: e7f1a2b3c4d5
Revises: d8e5b1c9f442
Create Date: 2026-08-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e7f1a2b3c4d5'
down_revision = 'd8e5b1c9f442'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'public_shares',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('file_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('files.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('share_token', sa.String(length=64), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('allow_download', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_public_shares_share_token', 'public_shares', ['share_token'], unique=True)
    op.create_index('ix_public_shares_file_id', 'public_shares', ['file_id'])


def downgrade() -> None:
    op.drop_index('ix_public_shares_file_id', table_name='public_shares')
    op.drop_index('ix_public_shares_share_token', table_name='public_shares')
    op.drop_table('public_shares')
