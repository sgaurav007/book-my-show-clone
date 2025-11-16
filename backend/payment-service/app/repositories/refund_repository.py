from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refund import Refund


class RefundRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, refund: Refund) -> Refund:
        self.db.add(refund)
        await self.db.commit()
        await self.db.refresh(refund)
        return refund

    async def find_by_id(self, refund_id: int) -> Optional[Refund]:
        result = await self.db.execute(select(Refund).filter(Refund.id == refund_id))
        return result.scalar_one_or_none()

    async def find_by_payment_id(self, payment_id: int) -> List[Refund]:
        result = await self.db.execute(select(Refund).filter(Refund.payment_id == payment_id))
        return list(result.scalars().all())

    async def update(self, refund: Refund) -> Refund:
        await self.db.commit()
        await self.db.refresh(refund)
        return refund
