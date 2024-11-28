from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.cart import Cart
from models.user import User
from models.product import Product
from models.db_session import session_db
from utils.message import msg

catalog_cart_router = Router()


@catalog_cart_router.callback_query(F.data.startswith("add_to_cart"))
@session_db
async def add_product_to_cart(callback: CallbackQuery, session: AsyncSession):
    """
    Добавление товара в корзину.
    """
    product_id = int(callback.data.split(":")[1])

    user = await User.get_user(telegram_id=callback.from_user.id, session=session)
    if not user:
        await callback.message.answer(msg("catalog", "3"))
        return

    product = await Product.get_product(product_id, session)
    if not product:
        await callback.message.answer(msg("catalog", "4"))
        return

    existing_cart_item = await session.execute(
        select(Cart).where(Cart.user_id == user.id, Cart.product_id == product_id)
    )
    if existing_cart_item.scalar():
        await callback.message.answer(msg("catalog", "5"))
        return

    cart_item = Cart(user_id=user.id, product_id=product_id)
    await cart_item.save(session)

    await callback.answer(msg("catalog", "6"))
    await callback.message.answer(
        msg("catalog", "7").format(product_name=product.name)
    )
    await callback.answer()
