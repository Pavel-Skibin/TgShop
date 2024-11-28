from typing import Self

from sqlalchemy import Column, Integer, ForeignKey, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from models import User
from models.db_session import Base


class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    date: Mapped[datetime] = mapped_column(default=datetime.now)
    sum: Mapped[int]
    type: Mapped[str]
    users: Mapped[list["User"]] = relationship(lazy="selectin")

    @classmethod
    async def get_transaction(cls, telegram_id: int, session: AsyncSession) -> Self:
        """
        Get transaction by telegram_id
        :param telegram_id: telegram_id
        :param session: database session
        :return: Transaction
        """
        _ = await session.execute(select(Transaction).join(User).where(User.telegram_id == telegram_id))
        return _.scalar()

    async def save(self, session: AsyncSession):
        session.add(self)
        await session.commit()

    @classmethod
    async def get_user_transactions(cls, telegram_id: int, session: AsyncSession):
        """
        Get all transactions for a user based on telegram_id
        :param telegram_id: user's telegram ID
        :param session: database session
        :return: List of transactions
        """
        result = await session.execute(
            select(Transaction).join(User).where(User.telegram_id == telegram_id)
        )
        return result.scalars().all()
