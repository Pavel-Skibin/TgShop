from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from keyboard.catalog import create_product_keyboard
from models.product import Product
from models.db_session import session_db
from utils.message import msg

catalog_navigation_router = Router()

@catalog_navigation_router.callback_query(F.data.in_({"prev_product", "next_product"}))
@session_db
async def navigate_products(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    """
    Листание товаров вперед/назад.
    """
    products = await Product.get_all_products(session)
    if not products:
        await callback.message.edit_text(msg("catalog", "1"))
        return

    data = await state.get_data()
    current_index = data.get('current_index', 0)

    if callback.data == "prev_product":
        current_index = (current_index - 1) % len(products)
    else:
        current_index = (current_index + 1) % len(products)

    await state.update_data(current_index=current_index)

    product = products[current_index]

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
