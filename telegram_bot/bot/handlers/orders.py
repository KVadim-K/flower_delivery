# telegram_bot/bot/handlers/orders.py

from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from telegram_bot.bot.states.order_states import OrderStates
from telegram_bot.bot.utils.api_client import APIClient, get_user_api_token, get_product_id_by_name
from telegram_bot.bot.keyboards.inline import confirm_order_kb

import logging
import os  # Для доступа к переменным окружения

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
    await message.answer("Загрузка доступных товаров...")

    # Проверка наличия активного заказа
    current_state = await state.get_state()
    if current_state and current_state != OrderStates.waiting_for_product_selection.state and current_state != OrderStates.waiting_for_quantity.state:
        logger.info(f"Пользователь {telegram_id} пытается создать новый заказ, но уже есть активный заказ.")
        await message.answer(
            "У вас уже есть активный заказ. Пожалуйста, завершите его или отмените перед созданием нового.")
        return

    await message.answer("Загрузка доступных товаров...")

    # Получение API-токена пользователя
    user_api_token = await get_user_api_token(telegram_id)
    if not user_api_token:
        logger.warning(f"Пользователь {telegram_id} не связан с учётной записью.")
        await message.answer("Ваш Telegram аккаунт не связан с учётной записью на сайте. Используйте /link для связывания.")
        return

    api_client = APIClient(token=user_api_token)
    logger.debug(f"APIClient инициализирован для пользователя {telegram_id}")

    try:
        # Получение списка продуктов через API
        products = await api_client.get_products()
        logger.debug(f"Получен список продуктов: {products}")
        if not products:
            logger.info(f"У пользователя {telegram_id} нет доступных товаров.")
            await message.answer("На данный момент нет доступных товаров для заказа.")
            return

        # Создание инлайн-клавиатуры с товарами
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=product['name'], callback_data=f"select_product:{product['id']}")]
                for product in products
            ],
            row_width=1
        )

        logger.debug(f"Инлайн-клавиатура с продуктами создана для пользователя {telegram_id}")
        await message.answer("Выберите товар из списка ниже:", reply_markup=keyboard)
        await state.set_state(OrderStates.waiting_for_product_selection)
        logger.info(f"Состояние пользователя {telegram_id} установлено на waiting_for_product_selection")
    except Exception as e:
        logger.exception(f"Ошибка при получении товаров для пользователя {telegram_id}: {e}")
        await message.answer("Произошла ошибка при получении списка товаров. Пожалуйста, попробуйте позже.")
    finally:
        await api_client.close()
        logger.debug(f"APIClient для пользователя {telegram_id} закрыт")

@router.callback_query(F.data.startswith("select_product:"))
async def select_product_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора продукта из инлайн-клавиатуры
    """
    telegram_id = callback.from_user.id
    product_id = callback.data.split(":")[1]
    logger.info(f"Пользователь {telegram_id} выбрал продукт с ID {product_id}.")

    await state.update_data(product_id=product_id)
    await state.set_state(OrderStates.waiting_for_quantity)

    await callback.message.edit_text("Введите количество:")
    await callback.answer()

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
    product_id = user_data.get('product_id')

    logger.info(f"Пользователь {telegram_id} заказал '{quantity}' единиц продукта с ID {product_id}.")

    # Получение API-токена пользователя
    user_api_token = await get_user_api_token(telegram_id)
    if not user_api_token:
        logger.warning(f"Пользователь {telegram_id} не связан с учётной записью.")
        await message.answer("Ваш Telegram аккаунт не связан с учётной записью на сайте. Используйте /link для связывания.")
        await state.clear()
        return

    api_client = APIClient(token=user_api_token)
    logger.debug(f"APIClient инициализирован для пользователя {telegram_id}")

    try:
        # Создание заказа через API
        order_response = await api_client.create_order([
            {"product": product_id, "quantity": quantity}
        ])
        logger.debug(f"Ответ от API после создания заказа: {order_response}")

        # Проверка наличия 'id' в ответе
        if 'id' not in order_response:
            logger.error(f"Ответ API не содержит 'id': {order_response}")
            await message.answer("Произошла ошибка при создании заказа. Пожалуйста, попробуйте позже.")
            return

        # Сохраняем order_id в состоянии для дальнейшего подтверждения (если необходимо)
        await state.update_data(order_id=order_response['id'])
        logger.info(f"Заказ №{order_response['id']} успешно создан для пользователя {telegram_id}.")
        await message.answer(
            f"Ваш заказ №{order_response['id']} успешно создан!",
            reply_markup=confirm_order_kb  # Добавляем клавиатуру с кнопками подтверждения (если требуется)
        )
        await state.set_state(OrderStates.active_order)  # Устанавливаем состояние активного заказа
        logger.info(f"Состояние пользователя {telegram_id} установлено на active_order")
    except Exception as e:
        logger.error(f"Ошибка при создании заказа для пользователя {telegram_id}: {e}")
        await message.answer(f"Произошла ошибка при создании заказа: {str(e)}")
    finally:
        await api_client.close()
        logger.debug(f"APIClient для пользователя {telegram_id} закрыт")

    # Теперь состояние очищается только после подтверждения заказа
