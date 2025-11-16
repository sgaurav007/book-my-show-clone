from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment_audit_log import PaymentAuditLog


class PaymentAuditLogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, audit_log: PaymentAuditLog) -> PaymentAuditLog:
        self.db.add(audit_log)
        await self.db.commit()
        await self.db.refresh(audit_log)
        return audit_log

    async def create(
        self, payment_id: int, event_type: str, event_data: Dict[str, Any]
    ) -> PaymentAuditLog:
        audit_log = PaymentAuditLog(
            payment_id=payment_id, event_type=event_type, event_data=event_data
        )
        return await self.save(audit_log)
