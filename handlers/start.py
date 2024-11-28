from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message

from keyboard.start import start_keyboard
from models.db_session import session_db
from sqlalchemy.ext.asyncio import AsyncSession

from models.transaction import Transaction
from models.user import User
from utils.message import msg

router = Router()


def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [ KeyboardButton(text="Мои покупки")]
        ],
        resize_keyboard=True
    )

@router.message(Command("start"))
@session_db
async def start_handler(message: types.Message, session: AsyncSession):
    if await User.get_user(message.from_user.id, session):
        await message.answer(msg("register", "2"), reply_markup=start_keyboard())
        await message.answer("Here are your options:", reply_markup=main_keyboard())
    else:
        await message.answer(text=msg("register", "1"), reply_markup=start_keyboard())
        await message.answer("Welcome! Here are your options:", reply_markup=main_keyboard())
        user = User(telegram_id=message.from_user.id, username=message.from_user.username,
                    first_name=message.from_user.first_name)
        await user.save(session)




@router.message(F.text == "Мои покупки")
@session_db
async def show_user_transactions(message: Message, session: AsyncSession):
    """
    Отображение списка транзакций пользователя через текстовое сообщение.
    """
    # Получаем telegram_id пользователя
    telegram_id = message.from_user.id

    # Получаем пользователя из базы данных
    user = await User.get_user(telegram_id=telegram_id, session=session)
    if not user:
        await message.answer("Пользователь не найден.")
        return

    # Получаем транзакции пользователя
    transactions = await Transaction.get_user_transactions(telegram_id, session)

    if not transactions:
        await message.answer("У вас нет транзакций.")
        return

    # Формируем сообщение с транзакциями
    transaction_list = "\n".join([
        f"Дата: {t.date.strftime('%Y-%m-%d %H:%M:%S')}, Сумма: {t.sum}, Тип: {t.type}"
        for t in transactions
    ])

    # Отправляем пользователю список транзакций
    await message.answer(transaction_list)
