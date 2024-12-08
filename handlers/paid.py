from datetime import datetime

from aiogram import Router, F, types
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from models.db_session import session_db
from models.payment import Payment
from models.transaction import Transaction
from utils.callback_factory import PaidCallbackFactory
from utils.check_paying_user import check_paying_user
from utils.message import msg

paid_router = Router()


@paid_router.callback_query(PaidCallbackFactory.filter())
@session_db
async def handle_payment_confirmation(callback: types.CallbackQuery, callback_data: PaidCallbackFactory,
                                      session: AsyncSession):
    """
    Обработка кнопки "Подтвердить оплату"
    """
    await callback.answer()
    if check_paying_user(str(callback_data.payment_id)):
        user = await User.get_user(telegram_id=callback.from_user.id, session=session)
        payment = await Payment.get_payment(payment_id=callback_data.payment_id, session=session)
        if payment.is_paid:
            await callback.message.answer(msg("paid", "2"))
            return
        payment.is_paid = True

        transaction = Transaction(
            user_id=user.id,
            sum=callback_data.sum,
            type="purchase",
            date=datetime.now()
        )

        await session.commit()
        await transaction.save(session)

        await callback.message.answer(f"Оплата успешно подтверждена на сумму {callback_data.sum}!")
    else:
        await callback.message.answer(msg("paid", "4"))
