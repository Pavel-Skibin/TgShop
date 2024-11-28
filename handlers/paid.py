
from aiogram import Router, F, types
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from models.db_session import session_db
from utils.cart_helpers import handle_payment_confirmation

paid_router = Router()


@paid_router.callback_query(F.data == "paid")
@session_db
async def handle_paid_button(callback: types.CallbackQuery,  session: AsyncSession):
    """
    Обработка кнопки "Оплачено"
    """
    await callback.answer()

    telegram_id = callback.from_user.id
    user_id = await User.get_user_id(telegram_id, session)

    await handle_payment_confirmation(callback, session, user_id)
