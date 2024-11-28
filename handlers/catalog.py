from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from keyboard.catalog import create_product_keyboard
from keyboard.start import start_keyboard
from models.product import Product
from models.db_session import session_db
from utils.message import msg

catalog_router = Router()


@catalog_router.callback_query(F.data == "catalog")
@session_db
async def show_catalog(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    """
    Отображение начальной карточки каталога.
    """
    products = await Product.get_all_products(session)
    if not products:
        await callback.message.edit_text(msg("catalog", "1"))
        return

    await state.update_data(current_index=0)
    product = products[0]

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=product.image_url,
            caption=msg("catalog", "2").format(
                product_name=product.name,
                price=product.price,
                description=product.description
            )
        ),
        reply_markup=create_product_keyboard(product.id)
    )
    await callback.answer()



@catalog_router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    """
    Возврат в главное меню с удалением сообщения.
    """
    try:
        await callback.message.delete()
        await callback.message.answer(
            msg("catalog", "8"),
            reply_markup=start_keyboard()
        )
    except TelegramBadRequest:
        await callback.message.edit_text(
            msg("catalog", "8"),
            reply_markup=start_keyboard()
        )
    await callback.answer()
