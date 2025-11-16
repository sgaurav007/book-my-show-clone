"""create movies table

Revision ID: 001
Revises: 
Create Date: 2024-01-01 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'movies',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('language', sa.String(length=50), nullable=False),
        sa.Column('release_date', sa.Date(), nullable=False),
        sa.Column('rating', sa.String(length=10), nullable=True),
        sa.Column('poster_url', sa.String(length=512), nullable=True),
        sa.Column('trailer_url', sa.String(length=512), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_movies_title', 'movies', ['title'])
    op.create_index('idx_movies_language', 'movies', ['language'])
    op.create_index('idx_movies_release_date', 'movies', ['release_date'])
    op.create_index('idx_movies_is_active', 'movies', ['is_active'])


def downgrade() -> None:
    op.drop_index('idx_movies_is_active', table_name='movies')
    op.drop_index('idx_movies_release_date', table_name='movies')
    op.drop_index('idx_movies_language', table_name='movies')
    op.drop_index('idx_movies_title', table_name='movies')
    op.drop_table('movies')
