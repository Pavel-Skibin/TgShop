from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.message import btn


def create_payment_keyboard(payment_url: str) -> InlineKeyboardMarkup:
    """
    Создание клавиатуры для оплаты.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=btn("paid","1"), url=payment_url)],
            [InlineKeyboardButton(text=btn("paid","2"), callback_data="paid")]
        ]
    )