from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from models.cart import Cart
from utils.cart_helpers import (
    send_total_sum_message,
    get_user_cart_items,
    update_total_sum,
)
from models.db_session import session_db
from keyboard.cart import create_cart_item_keyboard
from utils.message import msg

cart_router = Router()

@cart_router.callback_query(F.data == "cart")
@session_db
async def show_cart_callback(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    """
    Отображение корзины пользователя
    """
    user = await User.get_user(telegram_id=callback.from_user.id, session=session)
    if not user:
        await callback.message.answer(msg("cart", "1"))
        return

    cart_items = await get_user_cart_items(user.id, session)
    if not cart_items:
        await callback.message.answer(msg("cart", "2"))
        return

    total_sum = 0
    for item in cart_items:
        product = item.product
        if not product:
            continue

        total_price = product.price * item.quantity
        total_sum += total_price

        item_description_template = msg("cart", "item_description")
        caption = item_description_template.format(
            product_name=product.name,
            product_price=product.price,
            quantity=item.quantity,
            total_price=total_price
        )
        await callback.message.answer_photo(
            photo=product.image_url,
            caption=caption + "\n\n" + product.description,
            reply_markup=create_cart_item_keyboard(item.id)
        )

    await send_total_sum_message(total_sum, state, callback, session)
    await callback.answer()



@cart_router.callback_query(F.data.startswith("remove_from_cart"))
@session_db
async def remove_from_cart(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    """
    Удаление товара из корзины.
    """
    cart_item_id = int(callback.data.split(":")[1])

    cart_item = await Cart.get_cart_item(cart_item_id, session)
    if not cart_item:
        await callback.answer(msg("cart", "4"))
        return

    await session.delete(cart_item)
    await session.commit()
    await callback.message.delete()
    await update_total_sum(callback, session, state)

    await callback.answer(msg("cart", "8"))

