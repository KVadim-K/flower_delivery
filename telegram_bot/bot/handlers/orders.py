from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from telegram_bot.bot.states.order_states import OrderStates
from telegram_bot.bot.utils.api_client import APIClient, get_user_api_token
from telegram_bot.bot.keyboards.inline import confirm_order_kb

import logging
import aiohttp
import os  # Импортируем os для доступа к переменным окружения

logger = logging.getLogger(__name__)

router = Router()

# Получаем API_URL из переменных окружения
API_URL = os.getenv('API_URL')

if not API_URL:
    logger.error("API_URL не установлен в переменных окружения")
    raise EnvironmentError("API_URL не установлен в переменных окружения")

@router.message(Command(commands=["order"]))
async def cmd_order(message: Message, state: FSMContext):
    """
    Обработчик команды /order — инициирует процесс создания заказа
    """
    telegram_id = message.from_user.id
    logger.info(f"Пользователь {telegram_id} инициировал создание заказа.")
    await message.answer("Пожалуйста, введите название цветка, который вы хотите заказать:")
    await state.set_state(OrderStates.waiting_for_product)

@router.message(OrderStates.waiting_for_product, F.text)
async def process_product(message: Message, state: FSMContext):
    """
    Обработчик получения названия продукта
    """
    product_name = message.text.strip()
    telegram_id = message.from_user.id
    logger.info(f"Пользователь {telegram_id} выбрал продукт '{product_name}'.")
    await state.update_data(product_name=product_name)
    await message.answer("Введите количество:")
    await state.set_state(OrderStates.waiting_for_quantity)

@router.message(OrderStates.waiting_for_quantity, F.text)
async def process_quantity(message: Message, state: FSMContext):
    """
    Обработчик получения количества продукта и создания заказа
    """
    quantity_text = message.text.strip()
    telegram_id = message.from_user.id

    if not quantity_text.isdigit() or int(quantity_text) <= 0:
        logger.warning(f"Пользователь {telegram_id} ввёл некорректное количество: '{quantity_text}'.")
        await message.answer("Пожалуйста, введите корректное количество (целое число, большее 0):")
        return

    quantity = int(quantity_text)
    user_data = await state.get_data()
    product_name = user_data.get('product_name')

    logger.info(f"Пользователь {telegram_id} заказал '{quantity}' единиц продукта '{product_name}'.")

    # Получение ID продукта по названию через API Django
    product_id = await get_product_id_by_name(product_name)
    if not product_id:
        logger.warning(f"Продукт '{product_name}' не найден для пользователя {telegram_id}.")
        await message.answer(f"Продукт '{product_name}' не найден. Попробуйте снова.")
        await state.clear()
        return

    # Получение API-токена пользователя по Telegram ID
    user_api_token = await get_user_api_token(telegram_id)
    if not user_api_token:
        logger.warning(f"Пользователь {telegram_id} не связан с учётной записью.")
        await message.answer("Ваш Telegram аккаунт не связан с учётной записью на сайте. Используйте /link для связывания.")
        await state.clear()
        return

    api_client = APIClient(token=user_api_token)

    try:
        order_response = await api_client.create_order([
            {"product": product_id, "quantity": quantity}
        ])
        # Сохраняем order_id в состоянии для дальнейшего подтверждения
        await state.update_data(order_id=order_response['id'])
        logger.info(f"Заказ №{order_response['id']} успешно создан для пользователя {telegram_id}.")
        await message.answer(
            f"Ваш заказ №{order_response['id']} успешно создан!",
            reply_markup=confirm_order_kb  # Добавляем клавиатуру с кнопками подтверждения
        )
    except Exception as e:
        logger.error(f"Ошибка при создании заказа для пользователя {telegram_id}: {e}")
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
    search_url = f"{API_URL}/products/api/search/?search={product_name}"
    async with aiohttp.ClientSession() as session:
        async with session.get(search_url) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('results'):
                    product_id = data['results'][0]['id']
                    logger.info(f"Найден продукт '{product_name}' с ID {product_id}.")
                    return product_id
            logger.error(f"Продукт '{product_name}' не найден. Ответ API: {response.status}")
            return None
