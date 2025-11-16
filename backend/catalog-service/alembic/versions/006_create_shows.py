"""create shows table

Revision ID: 006
Revises: 005
Create Date: 2024-01-01 10:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'shows',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('movie_id', sa.BigInteger(), nullable=False),
        sa.Column('screen_id', sa.BigInteger(), nullable=False),
        sa.Column('start_time', sa.TIMESTAMP(), nullable=False),
        sa.Column('end_time', sa.TIMESTAMP(), nullable=False),
        sa.Column('base_price', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['movie_id'], ['movies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['screen_id'], ['screens.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_shows_movie_id', 'shows', ['movie_id'])
    op.create_index('idx_shows_screen_id', 'shows', ['screen_id'])
    op.create_index('idx_shows_start_time', 'shows', ['start_time'])


def downgrade() -> None:
    op.drop_index('idx_shows_start_time', table_name='shows')
    op.drop_index('idx_shows_screen_id', table_name='shows')
    op.drop_index('idx_shows_movie_id', table_name='shows')
    op.drop_table('shows')
