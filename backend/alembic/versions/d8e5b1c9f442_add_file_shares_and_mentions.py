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
    # 1. Safely create enum type if it does not already exist
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE share_permission AS ENUM ('view', 'comment', 'edit');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # 2. Create file_shares table with create_type=False so SQLAlchemy doesn't re-attempt creating the enum
    op.create_table(
        'file_shares',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('file_id', sa.UUID(), nullable=False),
        sa.Column('owner_id', sa.UUID(), nullable=False),
        sa.Column('shared_with_id', sa.UUID(), nullable=False),
        sa.Column('permission', postgresql.ENUM('view', 'comment', 'edit', name='share_permission', create_type=False), nullable=False),
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

    # 3. Safely add mentioned_user_ids column
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE comments ADD COLUMN mentioned_user_ids jsonb NOT NULL DEFAULT '[]'::jsonb;
        EXCEPTION
            WHEN duplicate_column THEN null;
        END $$;
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE comments DROP COLUMN IF EXISTS mentioned_user_ids")
    op.drop_index(op.f('ix_file_shares_shared_with_id'), table_name='file_shares', if_exists=True)
    op.drop_index(op.f('ix_file_shares_file_id'), table_name='file_shares', if_exists=True)
    op.drop_table('file_shares')
    op.execute("DROP TYPE IF EXISTS share_permission")
