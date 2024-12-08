
from utils.message import btn
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.callback_factory import PaidCallbackFactory  # Путь к вашему классу PaidCallbackFactory
from aiogram.types import InlineKeyboardMarkup


def create_payment_keyboard(payment_url: str, payment_id: int, sum: int) -> InlineKeyboardMarkup:
    """
    Создание клавиатуры для оплаты с использованием InlineKeyboardBuilder.
    """
    builder = InlineKeyboardBuilder()

    builder.button(text=btn("paid", "1"), url=payment_url)
    builder.button(
        text=btn("paid", "2"),
        callback_data=PaidCallbackFactory(payment_id=payment_id, sum=sum).pack()
    )
    builder.adjust(1)
    return builder.as_markup()
