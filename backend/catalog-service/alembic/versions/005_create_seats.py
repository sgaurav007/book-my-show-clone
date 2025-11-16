"""create seats table

Revision ID: 005
Revises: 004
Create Date: 2024-01-01 10:04:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'seats',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('row_label', sa.String(length=10), nullable=False),
        sa.Column('seat_number', sa.Integer(), nullable=False),
        sa.Column('seat_type', sa.String(length=20), nullable=False),
        sa.Column('screen_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['screen_id'], ['screens.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('screen_id', 'row_label', 'seat_number', name='uq_screen_row_seat')
    )
    op.create_index('idx_seats_screen_id', 'seats', ['screen_id'])
    op.create_index('idx_seats_row_label', 'seats', ['row_label'])


def downgrade() -> None:
    op.drop_index('idx_seats_row_label', table_name='seats')
    op.drop_index('idx_seats_screen_id', table_name='seats')
    op.drop_table('seats')
