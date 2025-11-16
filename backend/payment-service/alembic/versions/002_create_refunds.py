"""create refunds table

Revision ID: 002
Revises: 001
Create Date: 2025-11-16 10:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE TYPE refundstatus AS ENUM ('INITIATED', 'SUCCESS', 'FAILED')")
    
    op.create_table(
        'refunds',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('payment_id', sa.BigInteger(), nullable=False),
        sa.Column('refund_amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('refund_status', postgresql.ENUM('INITIATED', 'SUCCESS', 'FAILED', name='refundstatus'), nullable=False),
        sa.Column('refund_reference', sa.String(length=100), nullable=True),
        sa.Column('gateway_refund_id', sa.String(length=255), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['payment_id'], ['payments.id'], ondelete='CASCADE', name='fk_refund_payment'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_refunds_payment_id', 'refunds', ['payment_id'], unique=False)
    op.create_index('idx_refunds_refund_status', 'refunds', ['refund_status'], unique=False)
    op.create_index(op.f('ix_refunds_refund_reference'), 'refunds', ['refund_reference'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_refunds_refund_reference'), table_name='refunds')
    op.drop_index('idx_refunds_refund_status', table_name='refunds')
    op.drop_index('idx_refunds_payment_id', table_name='refunds')
    op.drop_table('refunds')
    op.execute("DROP TYPE refundstatus")
