"""create booking_seats table

Revision ID: 20250116_0002
Revises: 20250116_0001
Create Date: 2025-01-16 00:02:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250116_0002'
down_revision: Union[str, None] = '20250116_0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create booking_seats table
    op.create_table(
        'booking_seats',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('booking_id', sa.BigInteger(), nullable=False),
        sa.Column('seat_id', sa.BigInteger(), nullable=False),
        sa.Column('seat_number', sa.String(length=20), nullable=False),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='CASCADE')
    )
    
    # Create indexes
    op.create_index('idx_booking_id', 'booking_seats', ['booking_id'])
    op.create_index('idx_seat_id', 'booking_seats', ['seat_id'])
    
    # Create unique constraint
    op.create_unique_constraint('idx_booking_seat_unique', 'booking_seats', ['booking_id', 'seat_id'])


def downgrade() -> None:
    op.drop_table('booking_seats')
