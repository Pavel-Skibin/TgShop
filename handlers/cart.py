from aiogram import Router, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession

from models.cart import Cart
from models.product import Product
from models.user import User
from models.db_session import session_db

cart_router = Router()


def create_cart_item_keyboard(cart_item_id: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопкой удаления для элемента корзины.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Удалить", callback_data=f"remove_from_cart:{cart_item_id}")]
        ]
    )

@cart_router.callback_query(F.data == "cart")
@session_db
async def show_cart(callback: CallbackQuery, session: AsyncSession):
    """
    Отображение корзины пользователя.
    """
    user = await User.get_user(telegram_id=callback.from_user.id, session=session)
    if not user:
        await callback.message.answer("Вы не зарегистрированы!")
        return

    # Получаем элементы корзины пользователя
    cart_items = await Cart.get_user_cart_items(user.id, session)
    if not cart_items:
        # Проверяем, есть ли текст в сообщении
        if callback.message.text:
            await callback.message.edit_text("Ваша корзина пуста.")
        else:
            await callback.message.answer("Ваша корзина пуста.")
        return

    # Отображаем содержимое корзины
    total_sum = 0
    for item in cart_items:
        product = item.product
        if not product:
            continue

        total_sum += product.price
        await callback.message.answer_photo(
            photo=product.image_url,
            caption=f"<b>{product.name}</b>\nЦена: {product.price} руб.\n\n{product.description}",
            reply_markup=create_cart_item_keyboard(item.id)
        )

    # Выводим итоговую сумму
    await callback.message.answer(f"Сумма к оплате: <b>{total_sum} руб.</b>", parse_mode="HTML")
    await callback.answer()


@cart_router.callback_query(F.data.startswith("remove_from_cart"))
@session_db
async def remove_from_cart(callback: CallbackQuery, session: AsyncSession):
    """
    Удаление товара из корзины.
    """
    cart_item_id = int(callback.data.split(":")[1])

    cart_item = await Cart.get_cart_item(cart_item_id, session)
    if not cart_item:
        await callback.answer("Товар уже удален.")
        return

    await cart_item.delete(session)
    await callback.answer("Товар удален из корзины.")
    await callback.message.delete()
    await callback.answer()


@cart_router.callback_query(F.data.startswith("add_to_cart"))
@session_db
async def add_to_cart(callback: CallbackQuery, session: AsyncSession):
    """
    Добавление товара в корзину.
    """
    product_id = int(callback.data.split(":")[1])

    user = await User.get_user(telegram_id=callback.from_user.id, session=session)
    if not user:
        await callback.message.answer("Вы не зарегистрированы!")
        return

    cart_item = Cart(user_id=user.id, product_id=product_id)
    await cart_item.save(session)

    await callback.answer("Товар добавлен в корзину!")
    await callback.answer()
