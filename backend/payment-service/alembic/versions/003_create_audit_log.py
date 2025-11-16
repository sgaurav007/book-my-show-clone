"""create payment audit log table

Revision ID: 003
Revises: 002
Create Date: 2025-11-16 10:02:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'payment_audit_log',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('payment_id', sa.BigInteger(), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('event_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['payment_id'], ['payments.id'], ondelete='CASCADE', name='fk_audit_payment'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_audit_payment_id', 'payment_audit_log', ['payment_id'], unique=False)
    op.create_index('idx_audit_event_type', 'payment_audit_log', ['event_type'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_audit_event_type', table_name='payment_audit_log')
    op.drop_index('idx_audit_payment_id', table_name='payment_audit_log')
    op.drop_table('payment_audit_log')
