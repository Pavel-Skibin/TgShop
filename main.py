import asyncio
from aiogram import Dispatcher
from data.config import bot
from handlers import start
from handlers.admin_add import admin_router
from handlers.admin_edit import admin_router_edit
from handlers.cart import cart_router
from handlers.cart_quantity import cart_quantity_router
from handlers.catalog import catalog_router
from handlers.catalog_cart import catalog_cart_router
from handlers.catalog_navigation import catalog_navigation_router
from handlers.paid import paid_router
from models.db_session import global_init
from aiogram.fsm.storage.memory import MemoryStorage

dp = Dispatcher(storage=MemoryStorage())

dp.include_router(start.router)
dp.include_router(catalog_router)
dp.include_router(admin_router)
dp.include_router(cart_router)
dp.include_router(admin_router_edit)
dp.include_router(catalog_navigation_router)
dp.include_router(catalog_cart_router)
dp.include_router(cart_quantity_router)
dp.include_router(paid_router)

async def main():
    await global_init()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
