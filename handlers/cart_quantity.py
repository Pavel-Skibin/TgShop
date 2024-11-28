from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from models.cart import Cart
from models.db_session import session_db
from utils.message import msg
from utils.cart_helpers import update_total_sum
from keyboard.cart import create_cart_item_keyboard

cart_quantity_router = Router()

@cart_quantity_router.callback_query(F.data.startswith("increase_quantity"))
@session_db
async def increase_quantity(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    """
    Увеличение количества товара в корзине.
    """
    cart_item_id = int(callback.data.split(":")[1])

    cart_item = await Cart.get_cart_item(cart_item_id, session)
    if not cart_item:
        await callback.answer(msg("cart", "5"))
        return

    cart_item.quantity += 1
    await session.commit()

    product = cart_item.product
    new_caption = msg("cart", "item_description").format(
        product_name=product.name,
        product_price=product.price,
        quantity=cart_item.quantity,
        total_price=cart_item.quantity * product.price
    )

    await callback.message.edit_caption(
        caption=new_caption,
        reply_markup=create_cart_item_keyboard(cart_item.id),
        parse_mode="HTML"
    )
    await update_total_sum(callback, session, state)
    await callback.answer(msg("cart", "6"))


@cart_quantity_router.callback_query(F.data.startswith("decrease_quantity"))
@session_db
async def decrease_quantity(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    """
    Уменьшение количества товара в корзине.
    """
    cart_item_id = int(callback.data.split(":")[1])

    cart_item = await Cart.get_cart_item(cart_item_id, session)
    if not cart_item:
        await callback.answer(msg("cart", "5"))
        return

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        await session.commit()

        product = cart_item.product
        new_caption = msg("cart", "item_description").format(
            product_name=product.name,
            product_price=product.price,
            quantity=cart_item.quantity,
            total_price=cart_item.quantity * product.price
        )

        await callback.message.edit_caption(
            caption=new_caption,
            reply_markup=create_cart_item_keyboard(cart_item.id),
            parse_mode="HTML"
        )

        await update_total_sum(callback, session, state)
        await callback.answer(msg("cart", "7"))
    else:
        await session.delete(cart_item)
        await session.commit()
        await callback.message.delete()
        await update_total_sum(callback, session, state)
        await callback.answer(msg("cart", "8"))
