from aiogram import Router, types, F
from aiogram.filters import Command
from keyboard.main import main_keyboard
from keyboard.start import start_keyboard
from models.db_session import session_db
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from utils.message import msg

router = Router()

@router.message(Command("start"))
@session_db
async def start_handler(message: types.Message, session: AsyncSession):
    if await User.get_user(message.from_user.id, session):
        await message.answer(msg("register", "2"), reply_markup=start_keyboard())
        await message.answer(msg("register", "2"), reply_markup=main_keyboard())
    else:
        await message.answer(text=msg("register", "1"), reply_markup=start_keyboard())
        await message.answer(text=msg("register", "1"), reply_markup=main_keyboard())
        user = User(telegram_id=message.from_user.id, username=message.from_user.username,
                    first_name=message.from_user.first_name)
        await user.save(session)




