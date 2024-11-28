from datetime import datetime
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.cart import Cart
from models.payment import Payment
from models.transaction import Transaction
from models.user import User
from utils.generate_url import generate_url
from keyboard.paid import create_payment_keyboard
from utils.check_paying_user import check_paying_user
from utils.message import msg


async def send_total_sum_message(
        total_sum: int,
        state: FSMContext,
        callback: CallbackQuery,
        session: AsyncSession
):
    user_id = await User.get_user_id(
        telegram_id=callback.from_user.id,
        session=session
    )
    state_data = await state.get_data()
    total_sum_message_id = state_data.get("total_sum_message_id")
    previous_total_sum = state_data.get("previous_total_sum")
    if previous_total_sum == total_sum:
        return

    payment = Payment(
        user_id=user_id,
        sum=total_sum,
        is_paid=False,
        date=datetime.now()
    )
    session.add(payment)
    await session.commit()

    payment_url = generate_url(label=str(payment.id), amount=total_sum)
    payment_keyboard = create_payment_keyboard(payment_url)
    new_text = f"Итоговая сумма: {total_sum} руб."

    if total_sum_message_id:
        try:
            await callback.bot.edit_message_text(
                text=new_text,
                chat_id=callback.message.chat.id,
                message_id=total_sum_message_id,
                parse_mode="HTML",
                reply_markup=payment_keyboard
            )
        except Exception as e:
            print(f"Ошибка при обновлении сообщения с итоговой суммой: {e}")
    else:
        new_message = await callback.message.answer(
            new_text,
            parse_mode="HTML",
            reply_markup=payment_keyboard
        )
        await state.update_data(total_sum_message_id=new_message.message_id)

    await state.update_data(previous_total_sum=total_sum)


async def get_user_cart_items(user_id: int, session: AsyncSession):
    return await Cart.get_user_cart_items(user_id, session)


async def update_total_sum(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    """
    Обновление сообщения с общей суммой корзины.
    """
    user = await User.get_user(telegram_id=callback.from_user.id, session=session)
    if not user:
        return
    cart_items = await get_user_cart_items(user.id, session)
    total_sum = sum(item.product.price * item.quantity for item in cart_items if item.product)
    await send_total_sum_message(total_sum, state, callback, session)


async def handle_payment_confirmation(callback: CallbackQuery, session: AsyncSession, user_id: int):
    try:
        last_unpaid_payment = await Payment.get_last_unpaid_payment(user_id, session)
        last_unpaid_payment = last_unpaid_payment.scalar_one_or_none()
        if not last_unpaid_payment:
            await callback.message.answer(msg("paid", "1"))
            return

        if last_unpaid_payment.is_paid:
            await callback.message.answer(msg("paid", "2"))
            return

        if check_paying_user(str(last_unpaid_payment.id)):
            async with session.begin_nested():
                last_unpaid_payment = await session.merge(last_unpaid_payment)
                last_unpaid_payment.is_paid = True
                transaction = Transaction(
                    user_id=last_unpaid_payment.user_id,
                    sum=last_unpaid_payment.sum,
                    type="income",
                    date=datetime.now()
                )
                session.add(transaction)
                await session.commit()

            await callback.message.answer(msg("paid", "3"))
        else:
            await callback.message.answer(msg("paid", "4"))

    except Exception as e:
        await session.rollback()
        await callback.message.answer(msg("paid", "5").format(error=str(e)))
