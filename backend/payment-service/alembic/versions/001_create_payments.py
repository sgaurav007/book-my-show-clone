"""create payments table

Revision ID: 001
Revises: 
Create Date: 2025-11-16 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE TYPE paymentmethod AS ENUM ('CARD', 'UPI', 'NETBANKING', 'WALLET')")
    op.execute("CREATE TYPE paymentstatus AS ENUM ('INITIATED', 'SUCCESS', 'FAILED', 'REFUNDED')")
    
    op.create_table(
        'payments',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('payment_reference', sa.String(length=100), nullable=False),
        sa.Column('booking_id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=10), server_default='INR', nullable=True),
        sa.Column('payment_method', postgresql.ENUM('CARD', 'UPI', 'NETBANKING', 'WALLET', name='paymentmethod'), nullable=True),
        sa.Column('payment_status', postgresql.ENUM('INITIATED', 'SUCCESS', 'FAILED', 'REFUNDED', name='paymentstatus'), nullable=False),
        sa.Column('gateway_transaction_id', sa.String(length=255), nullable=True),
        sa.Column('gateway_name', sa.String(length=50), nullable=True),
        sa.Column('failure_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_payments_booking_id', 'payments', ['booking_id'], unique=True)
    op.create_index('idx_payments_user_id', 'payments', ['user_id'], unique=False)
    op.create_index('idx_payments_payment_status', 'payments', ['payment_status'], unique=False)
    op.create_index('idx_payments_payment_reference', 'payments', ['payment_reference'], unique=True)


def downgrade() -> None:
    op.drop_index('idx_payments_payment_reference', table_name='payments')
    op.drop_index('idx_payments_payment_status', table_name='payments')
    op.drop_index('idx_payments_user_id', table_name='payments')
    op.drop_index('idx_payments_booking_id', table_name='payments')
    op.drop_table('payments')
    op.execute("DROP TYPE paymentstatus")
    op.execute("DROP TYPE paymentmethod")
