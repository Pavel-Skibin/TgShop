from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from filters.admin_filter import AdminFilter
from keyboard.admin import create_action_keyboard
from models.product import Product
from models.db_session import session_db
from utils.message import msg

admin_router = Router()
admin_router.message.filter(AdminFilter())



ACTION_KB = create_action_keyboard()

class AddProductState(StatesGroup):
    name = State()
    description = State()
    price = State()
    image_url = State()


# Обработка команды /admin
@admin_router.message(Command("admin"))
async def admin_menu(message: types.Message):
    """
    Админское меню для добавления товара.
    """
    await message.answer(msg("admin", "menu"))


# Обработка команды для добавления товара
@admin_router.message(Command("add_product"))
async def start_add_product(message: types.Message, state: FSMContext):
    """
    Начало добавления товара.
    """
    await state.set_state(AddProductState.name)
    await message.answer(msg("admin", "add_product_start"), reply_markup=ACTION_KB)


@admin_router.message(StateFilter("*"), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Отмена текущего действия.
    """
    await state.clear()
    await message.answer(msg("admin", "cancel"), reply_markup=ReplyKeyboardRemove())



@admin_router.message(StateFilter("*"), F.text.casefold() == "назад")
async def back_handler(message: types.Message, state: FSMContext):
    """
    Возврат к предыдущему состоянию.
    """
    current_state = await state.get_state()

    if current_state == AddProductState.name.state:
        await message.answer(msg("admin", "back"))
        return

    previous_state = None
    for step in AddProductState.__all_states__:
        if step.state == current_state:
            if previous_state:
                await state.set_state(previous_state)
                await message.answer(msg("admin", "back2"))
                return
        previous_state = step

    await message.answer(msg("admin", "no_previous_step"), reply_markup=ACTION_KB)


# Ввод названия товара
@admin_router.message(StateFilter(AddProductState.name), F.text)
async def add_product_name(message: types.Message, state: FSMContext):
    """
    Обработка названия продукта.
    """
    await state.update_data(name=message.text)
    await state.set_state(AddProductState.description)
    await message.answer(msg("admin", "enter_description"), reply_markup=ACTION_KB)


# Ввод описания товара
@admin_router.message(StateFilter(AddProductState.description), F.text)
async def add_product_description(message: types.Message, state: FSMContext):
    """
    Обработка описания продукта.
    """
    await state.update_data(description=message.text)
    await state.set_state(AddProductState.price)
    await message.answer(msg("admin", "enter_price"), reply_markup=ACTION_KB)


# Ввод цены товара
@admin_router.message(StateFilter(AddProductState.price), F.text)
async def add_product_price(message: types.Message, state: FSMContext):
    """
    Обработка цены продукта.
    """
    try:
        price = int(message.text)
        if price < 0:
            raise ValueError("Цена должна быть положительным числом.")
        await state.update_data(price=price)
        await state.set_state(AddProductState.image_url)
        await message.answer(msg("admin", "enter_image"), reply_markup=ACTION_KB)
    except ValueError:
        await message.answer(msg("admin", "invalid_price"))


# Ввод изображения товара
@admin_router.message(StateFilter(AddProductState.image_url), F.photo)
@session_db
async def add_product_image_url(message: types.Message, state: FSMContext, session):
    """
    Обработка изображения продукта.
    """
    data = await state.get_data()
    photo = message.photo[-1].file_id
    data['image_url'] = photo

    product = Product(**data)
    await product.save(session)

    await message.answer(msg("admin", "product_added"), reply_markup=ReplyKeyboardRemove())
    await state.clear()

