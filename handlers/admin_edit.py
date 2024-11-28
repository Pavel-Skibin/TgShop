from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from filters.admin_filter import AdminFilter
from keyboard.admin import create_action_keyboard, create_product_keyboard
from models.product import Product
from models.db_session import session_db
from utils.message import msg

admin_router_edit = Router()
admin_router_edit.message.filter(AdminFilter())


ACTION_KB = create_action_keyboard()
class EditProductState(StatesGroup):
    product_id = State()
    name = State()
    description = State()
    price = State()
    image_url = State()


@admin_router_edit.message(Command("edit_delete_products"))
@session_db
async def show_products(message: types.Message, session: AsyncSession):
    """
    Отображение всех товаров с кнопками "Удалить" и "Изменить".
    """
    products = await Product.get_all_products(session)

    if not products:
        await message.answer(msg("admin", "no_products"))
        return

    for product in products:
        keyboard = create_product_keyboard(product.id)
        await message.answer(
            msg("admin", "show_products_header").format(
                name=product.name,
                price=product.price,
                description=product.description
            ),
            reply_markup=keyboard
        )


@admin_router_edit.callback_query(F.data.startswith("delete_"))
@session_db
async def delete_product(callback: types.CallbackQuery, session: AsyncSession):
    """
    Удаление товара из базы данных.
    """
    product_id = int(callback.data.split("_")[1])
    product = await Product.get_product(product_id, session)

    if not product:
        await callback.answer(msg("admin", "product_not_found"))
        return

    await session.delete(product)
    await session.commit()
    await callback.answer(msg("admin", "product_deleted"), show_alert=True)
    await callback.message.delete()


@admin_router_edit.callback_query(F.data.startswith("edit_"))
@session_db
async def edit_product_start(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    """
    Начало редактирования товара.
    """
    product_id = int(callback.data.split("_")[1])
    product = await Product.get_product(product_id, session)

    if not product:
        await callback.answer(msg("admin", "product_not_found"))
        return

    await state.update_data(product_id=product_id)

    await state.set_state(EditProductState.name)
    await callback.message.answer(msg("admin", "edit_name"), reply_markup=ACTION_KB)
    await callback.answer()


@admin_router_edit.message(StateFilter(EditProductState.name), F.text)
@session_db
async def edit_product_name(message: types.Message, state: FSMContext, session: AsyncSession):
    """
    Редактирование названия товара.
    """
    data = await state.get_data()
    product = await Product.get_product(data["product_id"], session)

    if message.text != ".":
        product.name = message.text
        await session.commit()

    await state.set_state(EditProductState.description)
    await message.answer(msg("admin", "edit_description"), reply_markup=ACTION_KB)


@admin_router_edit.message(StateFilter(EditProductState.description), F.text)
@session_db
async def edit_product_description(message: types.Message, state: FSMContext, session: AsyncSession):
    """
    Редактирование описания товара.
    """
    data = await state.get_data()
    product = await Product.get_product(data["product_id"], session)

    if message.text != ".":
        product.description = message.text
        await session.commit()

    await state.set_state(EditProductState.price)
    await message.answer(msg("admin", "edit_price"), reply_markup=ACTION_KB)


@admin_router_edit.message(StateFilter(EditProductState.price), F.text)
@session_db
async def edit_product_price(message: types.Message, state: FSMContext, session: AsyncSession):
    """
    Редактирование цены товара.
    """
    try:
        data = await state.get_data()
        product = await Product.get_product(data["product_id"], session)

        if message.text != ".":
            price = int(message.text)
            if price < 0:
                raise ValueError
            product.price = price
            await session.commit()

        await state.set_state(EditProductState.image_url)
        await message.answer(msg("admin", "edit_image"), reply_markup=ACTION_KB)
    except ValueError:
        await message.answer(msg("admin", "invalid_price"))


@admin_router_edit.message(StateFilter(EditProductState.image_url), F.photo | F.text)
@session_db
async def edit_product_image_url(message: types.Message, state: FSMContext, session: AsyncSession):
    """
    Редактирование изображения товара.
    """
    data = await state.get_data()
    product = await Product.get_product(data["product_id"], session)

    if message.text != ".":
        product.image_url = message.photo[-1].file_id
        await session.commit()

    await message.answer(msg("admin", "changes_saved"), reply_markup=ReplyKeyboardRemove())
    await state.clear()