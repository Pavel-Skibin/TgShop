from sqlalchemy import BigInteger, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from typing import Self, Optional

from models.db_session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    username: Mapped[Optional[str]] = mapped_column(default=None)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)

    @classmethod
    async def get_user(cls, telegram_id: int, session: AsyncSession) -> Self:
        """
        Get user by telegram id

        :param telegram_id: telegram id of user
        :param session: database session
        :return: User
        """
        _ = await session.execute(select(cls).where(cls.telegram_id == telegram_id))
        return _.scalar()

    @classmethod
    async def get_user_id(cls, telegram_id: int, session: AsyncSession) -> int:
        """
        Get user id by telegram id
        :param telegram_id: telegram id of user
        :param session: database session
        :return: user id
        """
        _ = await session.execute(select(cls.id).where(cls.telegram_id == telegram_id))
        return int(_.scalar())

    async def save(self, session: AsyncSession):
        session.add(self)
        await session.commit()
