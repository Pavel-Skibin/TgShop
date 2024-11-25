from sqlalchemy import BigInteger, Column, ForeignKey, Integer, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Self
from sqlalchemy.orm import joinedload

from models.db_session import Base
from models.product import Product
from models.user import User


class Cart(Base):
    __tablename__ = "cart"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"))

    product: Mapped[Product] = relationship("Product")

    @classmethod
    async def get_user_cart_items(cls, user_id: int, session: AsyncSession) -> list[Self]:
        """
        Получить все элементы корзины пользователя с жадной загрузкой связанных продуктов.

        :param user_id: ID пользователя
        :param session: сессия базы данных
        :return: список элементов корзины
        """
        result = await session.execute(
            select(cls).options(joinedload(cls.product)).where(cls.user_id == user_id)
        )
        return result.scalars().all()
    @classmethod
    async def get_cart_item(cls, cart_item_id: int, session: AsyncSession) -> Self | None:
        """
        Получить элемент корзины по ID.

        :param cart_item_id: ID элемента корзины
        :param session: сессия базы данных
        :return: элемент корзины
        """
        result = await session.execute(select(cls).where(cls.id == cart_item_id))
        return result.scalar()

    async def delete(self, session: AsyncSession):
        """
        Удалить элемент корзины.

        :param session: сессия базы данных
        """
        await session.delete(self)
        await session.commit()

    async def save(self, session: AsyncSession):
        """
        Сохранить элемент корзины.

        :param session: сессия базы данных
        """
        session.add(self)
        await session.commit()
