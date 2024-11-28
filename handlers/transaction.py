from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from models.db_session import session_db
from models.transaction import Transaction

router = Router()

@router.message(F.text == "Мои покупки")
@session_db
async def show_user_transactions(message: Message, session: AsyncSession):
    """
    Отображение списка транзакций пользователя через текстовое сообщение.
    """
    telegram_id = message.from_user.id

    user = await User.get_user(telegram_id=telegram_id, session=session)
    if not user:
        await message.answer("Пользователь не найден.")
        return

    transactions = await Transaction.get_user_transactions(telegram_id, session)

    if not transactions:
        await message.answer("У вас нет транзакций.")
        return
    transaction_list = "\n".join([
        f"Дата: {t.date.strftime('%Y-%m-%d %H:%M:%S')}, Сумма: {t.sum}, Тип: {t.type}"
        for t in transactions
    ])

    await message.answer(transaction_list)