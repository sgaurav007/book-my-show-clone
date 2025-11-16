from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class PaymentAuditLog(Base):
    __tablename__ = "payment_audit_log"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    payment_id = Column(BigInteger, ForeignKey("payments.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    event_data = Column(JSONB, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
