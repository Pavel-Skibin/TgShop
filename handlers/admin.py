from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from models.product import Product
from models.db_session import session_db

# Создаем роутер для админских команд
admin_router = Router()


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
    await message.answer(
        "Добро пожаловать в админский режим!\nДля добавления товара введите /add_product."
    )


# Обработка команды для добавления товара
@admin_router.message(Command("add_product"))
async def start_add_product(message: types.Message, state: FSMContext):
    """
    Начало добавления товара.
    """
    await state.set_state(AddProductState.name)
    await message.answer("Введите название продукта:")


# Ввод названия товара
@admin_router.message(StateFilter(AddProductState.name))
async def add_product_name(message: types.Message, state: FSMContext):
    """
    Обработка названия продукта.
    """
    await state.update_data(name=message.text)
    await state.set_state(AddProductState.description)
    await message.answer("Введите описание продукта:")


# Ввод описания товара
@admin_router.message(StateFilter(AddProductState.description))
async def add_product_description(message: types.Message, state: FSMContext):
    """
    Обработка описания продукта.
    """
    await state.update_data(description=message.text)
    await state.set_state(AddProductState.price)
    await message.answer("Введите цену продукта (в целых числах):")


# Ввод цены товара
@admin_router.message(StateFilter(AddProductState.price))
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
        await message.answer("Загрузите изображение продукта:")
    except ValueError:
        await message.answer("Цена должна быть положительным целым числом. Попробуйте еще раз:")


# Ввод изображения товара
@admin_router.message(StateFilter(AddProductState.image_url), F.photo)
@session_db
async def add_product_image_url(message: types.Message, state: FSMContext, session):
    """
    Обработка изображения продукта.
    """
    data = await state.get_data()
    photo = message.photo[-1].file_id  # Получаем file_id последней фотографии
    data['image_url'] = photo

    # Создаем объект продукта и сохраняем в базу
    product = Product(**data)
    await product.save(session)

    await message.answer("Продукт успешно добавлен в базу данных!")
    await state.clear()
