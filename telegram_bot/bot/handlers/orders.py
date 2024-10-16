from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from telegram_bot.bot.states.order_states import OrderStates
from telegram_bot.bot.utils.api_client import APIClient, get_user_api_token
from telegram_bot.bot.keyboards.inline import confirm_order_kb

import os
import aiohttp
from dotenv import load_dotenv

load_dotenv()

router = Router()

@router.message(Command(commands=["order"]))
async def cmd_order(message: Message, state: FSMContext):
    """
    Обработчик команды /order — инициирует процесс создания заказа
    """
    await message.answer("Пожалуйста, введите название цветка, который вы хотите заказать:")
    await state.set_state(OrderStates.waiting_for_product)

@router.message(OrderStates.waiting_for_product, F.text)
async def process_product(message: Message, state: FSMContext):
    """
    Обработчик получения названия продукта
    """
    product_name = message.text.strip()
    await state.update_data(product_name=product_name)
    await message.answer("Введите количество:")
    await state.set_state(OrderStates.waiting_for_quantity)

@router.message(OrderStates.waiting_for_quantity, F.text)
async def process_quantity(message: Message, state: FSMContext):
    """
    Обработчик получения количества продукта и создания заказа
    """
    quantity_text = message.text.strip()
    if not quantity_text.isdigit() or int(quantity_text) <= 0:
        await message.answer("Пожалуйста, введите корректное количество (целое число, большее 0):")
        return
    quantity = int(quantity_text)
    user_data = await state.get_data()
    product_name = user_data.get('product_name')

    # Получение ID продукта по названию через API Django
    product_id = await get_product_id_by_name(product_name)
    if not product_id:
        await message.answer(f"Продукт '{product_name}' не найден. Попробуйте снова.")
        await state.clear()
        return

    # Получение API-токена пользователя по Telegram ID
    user_api_token = await get_user_api_token(message.from_user.id)
    if not user_api_token:
        await message.answer("Ваш Telegram аккаунт не связан с учётной записью на сайте. Используйте /link для связывания.")
        await state.clear()
        return

    api_client = APIClient(token=user_api_token)

    try:
        order_response = await api_client.create_order([
            {"product": product_id, "quantity": quantity}
        ])
        await message.answer(
            f"Ваш заказ №{order_response['id']} успешно создан!",
            reply_markup=confirm_order_kb  # Добавляем клавиатуру с кнопками подтверждения
        )
    except Exception as e:
        await message.answer(f"Произошла ошибка при создании заказа: {str(e)}")
    finally:
        await api_client.close()

    await state.clear()

# Вспомогательные функции

async def get_product_id_by_name(product_name: str) -> int:
    """
    Функция для получения ID продукта по его названию через API Django.
    Предполагается наличие эндпоинта /products/api/search/?search=<name>
    """
    API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
    search_url = f"{API_URL}/products/api/search/?search={product_name}"
    async with aiohttp.ClientSession() as session:
        async with session.get(search_url) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('results'):
                    return data['results'][0]['id']
            return None
