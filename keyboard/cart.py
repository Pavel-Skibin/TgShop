from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.message import btn


def create_cart_item_keyboard(cart_item_id: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками изменения количества для элемента корзины.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=btn("cart","2"), callback_data=f"decrease_quantity:{cart_item_id}"),
                InlineKeyboardButton(text=btn("cart","1"), callback_data=f"increase_quantity:{cart_item_id}")
            ],
            [InlineKeyboardButton(text=btn("cart","3"), callback_data=f"remove_from_cart:{cart_item_id}")]
        ]
    )