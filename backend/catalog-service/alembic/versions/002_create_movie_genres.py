"""create movie_genres table

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 10:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'movie_genres',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('movie_id', sa.BigInteger(), nullable=False),
        sa.Column('genre', sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(['movie_id'], ['movies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_movie_genres_movie_id', 'movie_genres', ['movie_id'])
    op.create_index('idx_movie_genres_genre', 'movie_genres', ['genre'])


def downgrade() -> None:
    op.drop_index('idx_movie_genres_genre', table_name='movie_genres')
    op.drop_index('idx_movie_genres_movie_id', table_name='movie_genres')
    op.drop_table('movie_genres')
