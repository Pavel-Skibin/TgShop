from typing import Self

from sqlalchemy import Column, Integer, ForeignKey, select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from models.db_session import Base


class Payment(Base):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    date: Mapped[datetime] = mapped_column(default=datetime.now)
    sum: Mapped[int]
    is_paid: Mapped[bool] = mapped_column(default=False)

    @classmethod
    async def get_payment(cls, payment_id: int, session: AsyncSession) -> Self:
        """
        get payment by payment id
        :param payment_id: payment id
        :param session: database session
        :return: Payment
        """
        _ = await session.execute(select(Payment).where(cls.id == payment_id))
        return _.scalar()

    @classmethod
    async def get_count_payments(cls, user_id: int, session: AsyncSession) -> int:
        """
        get count payments by telegram_id
        :param user_id: id of user
        :param session: database session
        :return: count payments
        """
        _ = await session.execute(select(func.count(cls.id)).where(cls.user_id == user_id, cls.is_paid == True))
        return int(_.scalar())

    async def save(self, session: AsyncSession):
        session.add(self)
        await session.commit()


