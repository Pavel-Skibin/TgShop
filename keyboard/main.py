from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [ KeyboardButton(text="Мои покупки")]
        ],
        resize_keyboard=True
    )