from sqlalchemy import BigInteger, select, Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from typing import Self, List

from models.db_session import Base


class Product(Base):
    __tablename__ = "product"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    price: Mapped[int] = mapped_column(Integer)
    image_url: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)

    @classmethod
    async def get_product(cls, product_id: int, session: AsyncSession) -> Self:
        """
        Получить продукт по ID.

        :param product_id: ID продукта
        :param session: сессия базы данных
        :return: экземпляр Product
        """
        result = await session.execute(select(cls).where(cls.id == product_id))
        return result.scalar()

    @classmethod
    async def get_all_products(cls, session: AsyncSession) -> List[Self]:
        """
        Получить все продукты.

        :param session: сессия базы данных
        :return: список продуктов
        """
        result = await session.execute(select(cls))
        return result.scalars().all()

    async def save(self, session: AsyncSession):
        """
        Сохранить продукт в базе данных.

        :param session: сессия базы данных
        """
        session.add(self)
        await session.commit()
