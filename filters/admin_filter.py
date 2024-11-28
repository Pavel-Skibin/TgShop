from aiogram.filters import BaseFilter
from aiogram.types import Message

from data.config import ADMINS


class AdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.username in ADMINS
