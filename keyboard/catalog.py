from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.callback_factory import CatalogNavigationCallbackFactory
from utils.message import btn

from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_product_keyboard(product_id: int) -> InlineKeyboardMarkup:
    """
    Создаем клавиатуру для карточки товара.
    """
    builder = InlineKeyboardBuilder()

    builder.button(
        text=btn("catalog", "1"),
        callback_data=CatalogNavigationCallbackFactory(action="prev")
    )
    builder.button(
        text=btn("catalog", "2"),
        callback_data=CatalogNavigationCallbackFactory(action="next")
    )
    builder.button(
        text=btn("catalog", "4"),
        callback_data=f"add_to_cart:{product_id}"
    )
    builder.button(
        text=btn("catalog", "3"),
        callback_data="back_to_menu"
    )

    builder.adjust(2)
    return builder.as_markup()
