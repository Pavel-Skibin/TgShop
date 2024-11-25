from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.message import btn


def create_product_keyboard(product_id: int) -> InlineKeyboardMarkup:
    """
    Создаем клавиатуру для карточки товара.
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=btn("catalog", "4"), callback_data=f"add_to_cart:{product_id}")],
        [
            InlineKeyboardButton(text=btn("catalog", "1"), callback_data="prev_product"),
            InlineKeyboardButton(text=btn("catalog", "2"), callback_data="next_product")
        ],
        [InlineKeyboardButton(text=btn("catalog", "3"), callback_data="back_to_menu")]
    ])
