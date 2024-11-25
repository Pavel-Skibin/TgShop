from aiogram import Router, types, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext  # Импортируем правильный модуль для работы с состоянием FSM
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from keyboard.catalog import create_product_keyboard
from keyboard.start import start_keyboard
from models import User
from models.cart import Cart
from models.product import Product
from models.db_session import session_db

catalog_router = Router()


@catalog_router.callback_query(F.data == "catalog")
@session_db
async def show_catalog(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    """
    Отображение начальной карточки каталога.
    """
    products = await Product.get_all_products(session)
    if not products:
        await callback.message.edit_text("Каталог пуст.")
        return

    # Храним индекс текущего товара в состоянии
    await state.update_data(current_index=0)
    product = products[0]

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=product.image_url,
            caption=f"<b>{product.name}</b>\nЦена: {product.price} руб.\n\n{product.description}"
        ),
        reply_markup=create_product_keyboard(product.id)
    )
    await callback.answer()


@catalog_router.callback_query(F.data.in_({"prev_product", "next_product"}))
@session_db
async def navigate_products(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    """
    Листание товаров вперед/назад.
    """
    products = await Product.get_all_products(session)
    if not products:
        await callback.message.edit_text("Каталог пуст.")
        return

    data = await state.get_data()
    current_index = data.get('current_index', 0)

    # Обновляем индекс текущего товара
    if callback.data == "prev_product":
        current_index = (current_index - 1) % len(products)
    else:
        current_index = (current_index + 1) % len(products)

    await state.update_data(current_index=current_index)

    product = products[current_index]

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=product.image_url,
            caption=f"<b>{product.name}</b>\nЦена: {product.price} руб.\n\n{product.description}"
        ),
        reply_markup=create_product_keyboard(product.id)
    )
    await callback.answer()


@catalog_router.callback_query(F.data.startswith("add_to_cart"))
@session_db
async def add_product_to_cart(callback: CallbackQuery, session: AsyncSession):
    """
    Добавление товара в корзину.
    """
    product_id = int(callback.data.split(":")[1])

    # Получаем текущего пользователя из базы данных
    user = await User.get_user(telegram_id=callback.from_user.id, session=session)
    if not user:
        await callback.message.answer("Вы не зарегистрированы!")
        return

    # Проверяем, существует ли продукт
    product = await Product.get_product(product_id, session)
    if not product:
        await callback.message.answer("Товар не найден!")
        return

    # Проверяем, не добавлен ли уже этот товар в корзину пользователя
    existing_cart_item = await session.execute(
        select(Cart).where(Cart.user_id == user.id, Cart.product_id == product_id)
    )
    if existing_cart_item.scalar():
        await callback.message.answer("Этот товар уже есть в вашей корзине.")
        return

    # Создаем и сохраняем элемент корзины
    cart_item = Cart(user_id=user.id, product_id=product_id)
    await cart_item.save(session)

    # Уведомляем пользователя
    await callback.answer("Товар добавлен в корзину!")
    await callback.message.answer(f"Товар '{product.name}' добавлен в вашу корзину!")
    await callback.answer()

@catalog_router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    """
    Возврат в главное меню.
    """
    try:
        await callback.message.edit_text(
            "Вы вернулись в главное меню.",
            reply_markup=start_keyboard()
        )
    except TelegramBadRequest:
        await callback.message.edit_reply_markup(
            reply_markup=start_keyboard()
        )
    await callback.answer()
