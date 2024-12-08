from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.message import btn


def start_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text=btn("start", "1"), callback_data="catalog"),
         InlineKeyboardButton(text=btn("start", "2"), callback_data="cart")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
