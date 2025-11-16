"""create bookings table

Revision ID: 20250116_0001
Revises: 
Create Date: 2025-01-16 00:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250116_0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create booking_status_enum type
    op.execute("CREATE TYPE booking_status_enum AS ENUM ('PENDING', 'CONFIRMED', 'CANCELLED', 'EXPIRED')")
    
    # Create bookings table
    op.create_table(
        'bookings',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('booking_reference', sa.String(length=100), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('show_id', sa.BigInteger(), nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('booking_status', sa.Enum('PENDING', 'CONFIRMED', 'CANCELLED', 'EXPIRED', name='booking_status_enum', create_type=False), nullable=False),
        sa.Column('payment_id', sa.BigInteger(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_booking_reference', 'bookings', ['booking_reference'])
    op.create_index('idx_user_id', 'bookings', ['user_id'])
    op.create_index('idx_show_id', 'bookings', ['show_id'])
    op.create_index('idx_booking_status', 'bookings', ['booking_status'])
    op.create_index('idx_expires_at', 'bookings', ['expires_at'])
    
    # Create unique constraint
    op.create_unique_constraint('uq_booking_reference', 'bookings', ['booking_reference'])


def downgrade() -> None:
    op.drop_table('bookings')
    op.execute("DROP TYPE booking_status_enum")
