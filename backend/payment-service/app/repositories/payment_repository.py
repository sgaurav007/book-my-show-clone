from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment


class PaymentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, payment: Payment) -> Payment:
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)
        return payment

    async def find_by_id(self, payment_id: int) -> Optional[Payment]:
        result = await self.db.execute(select(Payment).filter(Payment.id == payment_id))
        return result.scalar_one_or_none()

    async def find_by_payment_reference(self, payment_reference: str) -> Optional[Payment]:
        result = await self.db.execute(
            select(Payment).filter(Payment.payment_reference == payment_reference)
        )
        return result.scalar_one_or_none()

    async def find_by_booking_id(self, booking_id: int) -> Optional[Payment]:
        result = await self.db.execute(select(Payment).filter(Payment.booking_id == booking_id))
        return result.scalar_one_or_none()

    async def exists_by_booking_id(self, booking_id: int) -> bool:
        result = await self.db.execute(
            select(Payment.id).filter(Payment.booking_id == booking_id)
        )
        return result.scalar_one_or_none() is not None

    async def update(self, payment: Payment) -> Payment:
        await self.db.commit()
        await self.db.refresh(payment)
        return payment
