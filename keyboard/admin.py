from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from utils.message import btn, msg


def create_action_keyboard() -> ReplyKeyboardMarkup:

    cancel_button = KeyboardButton(text=btn("admin","4"))
    back_button = KeyboardButton(text=btn("admin","3"))
    return ReplyKeyboardMarkup(keyboard=[[cancel_button, back_button]], resize_keyboard=True)


def create_product_keyboard(product_id: int) -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=btn("admin", "2"), callback_data=f"edit_{product_id}")],
        [InlineKeyboardButton(text=btn("admin", "1"), callback_data=f"delete_{product_id}")]
    ])
