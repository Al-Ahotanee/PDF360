"""add file_shares and comment mentions

Revision ID: d8e5b1c9f442
Revises: c7d2f4a8e331
Create Date: 2026-08-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd8e5b1c9f442'
down_revision = 'c7d2f4a8e331'
branch_labels = None
depends_on = None


def upgrade() -> None:
    share_perm_enum = postgresql.ENUM('view', 'comment', 'edit', name='share_permission')
    share_perm_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'file_shares',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('file_id', sa.UUID(), nullable=False),
        sa.Column('owner_id', sa.UUID(), nullable=False),
        sa.Column('shared_with_id', sa.UUID(), nullable=False),
        sa.Column('permission', sa.Enum('view', 'comment', 'edit', name='share_permission'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['file_id'], ['files.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['shared_with_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('file_id', 'shared_with_id', name='uq_file_shares_file_user'),
    )
    op.create_index(op.f('ix_file_shares_file_id'), 'file_shares', ['file_id'], unique=False)
    op.create_index(op.f('ix_file_shares_shared_with_id'), 'file_shares', ['shared_with_id'], unique=False)

    op.add_column(
        'comments',
        sa.Column('mentioned_user_ids', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
    )


def downgrade() -> None:
    op.drop_column('comments', 'mentioned_user_ids')
    op.drop_index(op.f('ix_file_shares_shared_with_id'), table_name='file_shares')
    op.drop_index(op.f('ix_file_shares_file_id'), table_name='file_shares')
    op.drop_table('file_shares')
    op.execute("DROP TYPE IF EXISTS share_permission")
