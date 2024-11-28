from sqlalchemy import Column, ForeignKey, Integer, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, joinedload

from models.db_session import Base
from models.product import Product
from models.user import User


class Cart(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    quantity = Column(Integer, default=1)

    product = relationship("Product")
    user = relationship("User")

    @classmethod
    async def get_user_cart_items(cls, user_id: int, session: AsyncSession):
        """
        Получить элементы корзины пользователя с продуктами.
        """
        result = await session.execute(
            select(cls).options(joinedload(cls.product)).where(cls.user_id == user_id)
        )
        return result.scalars().all()

    @classmethod
    async def get_existing_cart_item(cls, user_id: int, product_id: int, session: AsyncSession):
        """
        Проверить, существует ли товар в корзине пользователя.
        """
        result = await session.execute(
            select(cls).where(cls.user_id == user_id, cls.product_id == product_id)
        )
        return result.scalar_one_or_none()

    @classmethod
    async def get_cart_item(cls, cart_item_id: int, session: AsyncSession):
        """
           Получить элемент корзины с предварительной загрузкой связанных данных.
           """
        result = await session.execute(
            select(cls)
            .options(joinedload(cls.product))  # Предварительная загрузка продукта
            .where(cls.id == cart_item_id)
        )
        return result.scalar()

    async def save(self, session: AsyncSession):
        """
        Сохранить элемент корзины.
        """
        session.add(self)
        await session.commit()




