# telegram_bot/bot/handlers/orders.py

from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from telegram_bot.bot.states.order_states import OrderStates
from telegram_bot.bot.utils.api_client import APIClient, get_user_api_token, get_product_id_by_name
from telegram_bot.bot.keyboards.inline import confirm_order_kb, navigation_kb

import logging
import os  # Для доступа к переменным окружения
import re  # Для валидации ввода

logger = logging.getLogger(__name__)

router = Router()

# Получаем API_URL из переменных окружения
API_URL = os.getenv('API_URL')

if not API_URL:
    logger.error("API_URL не установлен в переменных окружения")
    raise EnvironmentError("API_URL не установлен в переменных окружения")


async def initiate_order_creation(source, state: FSMContext):
    """
    Общая функция для инициации создания заказа, вызываемая из команды /order и кнопки "Создать заказ"
    :param source: объект Message или CallbackQuery
    :param state: объект FSMContext
    """
    if isinstance(source, Message):
        send_message = source.answer
        user = source.from_user
    elif isinstance(source, CallbackQuery):
        send_message = source.message.edit_text
        user = source.from_user
    else:
        logger.error("Неизвестный тип источника для инициирования заказа")
        return

    telegram_id = user.id
    logger.debug(f"Инициация создания заказа для пользователя {telegram_id}")
    await send_message("Загрузка доступных товаров...")

    # Получение API-токена пользователя
    user_api_token = await get_user_api_token(telegram_id)
    if not user_api_token:
        logger.warning(f"Пользователь {telegram_id} не связан с учётной записью.")
        await send_message("Ваш Telegram аккаунт не связан с учётной записью на сайте. Используйте /link для связывания.")
        return

    # Проверка наличия активного заказа
    current_state = await state.get_state()
    if current_state and current_state not in [
        OrderStates.waiting_for_product_selection.state,
        OrderStates.waiting_for_quantity.state,
    ]:
        logger.info(f"Пользователь {telegram_id} пытается создать новый заказ, но уже есть активный заказ.")
        await send_message(
            "У вас уже есть активный заказ. Пожалуйста, завершите его или отмените перед созданием нового."
        )
        return

    api_client = APIClient(token=user_api_token)
    logger.debug(f"APIClient инициализирован для пользователя {telegram_id}")

    try:
        # Получение списка продуктов через API
        products = await api_client.get_products()
        logger.debug(f"Получен список продуктов: {products}")
        if not products:
            logger.info(f"У пользователя {telegram_id} нет доступных товаров.")
            await send_message("На данный момент нет доступных товаров для заказа.")
            return

        # Создание инлайн-клавиатуры с товарами
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=product['name'],
                        callback_data=f"select_product:{product['id']}"
                    )
                ]
                for product in products
            ],
            row_width=1
        )

        logger.debug(f"Инлайн-клавиатура с продуктами создана для пользователя {telegram_id}")
        await send_message("Выберите товар из списка ниже:", reply_markup=keyboard)
        await state.set_state(OrderStates.waiting_for_product_selection)
        logger.info(f"Состояние пользователя {telegram_id} установлено на waiting_for_product_selection")
    except Exception as e:
        logger.exception(f"Ошибка при получении товаров для пользователя {telegram_id}: {e}")
        await send_message("Произошла ошибка при получении списка товаров. Пожалуйста, попробуйте позже.")
    finally:
        await api_client.close()
        logger.debug(f"APIClient для пользователя {telegram_id} закрыт")


@router.message(Command(commands=["order"]))
async def cmd_order(message: Message, state: FSMContext):
    """
    Обработчик команды /order — инициирует процесс создания заказа
    """
    await initiate_order_creation(message, state)


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
    Обработчик получения количества продукта и перехода к вводу адреса доставки
    """
    quantity_text = message.text.strip()
    telegram_id = message.from_user.id

    if not quantity_text.isdigit() or int(quantity_text) <= 0:
        logger.warning(f"Пользователь {telegram_id} ввёл некорректное количество: '{quantity_text}'.")
        await message.answer("Пожалуйста, введите корректное количество (целое число, большее 0):")
        return

    quantity = int(quantity_text)
    await state.update_data(quantity=quantity)
    logger.info(f"Пользователь {telegram_id} заказал '{quantity}' единиц продукта.")

    await message.answer("Введите адрес доставки:")
    await state.set_state(OrderStates.waiting_for_address)
    logger.info(f"Состояние пользователя {telegram_id} установлено на waiting_for_address")


@router.message(OrderStates.waiting_for_address, F.text)
async def process_address(message: Message, state: FSMContext):
    """
    Обработчик получения адреса доставки и перехода к вводу города
    """
    address = message.text.strip()
    telegram_id = message.from_user.id

    # Простая валидация адреса
    if len(address.split()) < 2:
        logger.warning(f"Пользователь {telegram_id} ввёл некорректный адрес: '{address}'.")
        await message.answer("Пожалуйста, укажите полный адрес, включая улицу и номер дома:")
        return

    await state.update_data(address=address)
    logger.info(f"Пользователь {telegram_id} ввёл адрес доставки: {address}")

    await message.answer("Введите город:")
    await state.set_state(OrderStates.waiting_for_city)
    logger.info(f"Состояние пользователя {telegram_id} установлено на waiting_for_city")


@router.message(OrderStates.waiting_for_city, F.text)
async def process_city(message: Message, state: FSMContext):
    """
    Обработчик получения города и перехода к вводу почтового индекса
    """
    city = message.text.strip()
    telegram_id = message.from_user.id

    # Валидация города (только буквы, пробелы, дефисы)
    if not re.match(r'^[A-Za-zА-Яа-яЁё\s-]+$', city):
        logger.warning(f"Пользователь {telegram_id} ввёл некорректный город: '{city}'.")
        await message.answer("Город может содержать только буквы, пробелы и дефисы. Пожалуйста, введите город:")
        return

    await state.update_data(city=city)
    logger.info(f"Пользователь {telegram_id} ввёл город: {city}")

    await message.answer("Введите почтовый индекс (6 цифр):")
    await state.set_state(OrderStates.waiting_for_postal_code)
    logger.info(f"Состояние пользователя {telegram_id} установлено на waiting_for_postal_code")


@router.message(OrderStates.waiting_for_postal_code, F.text)
async def process_postal_code(message: Message, state: FSMContext):
    """
    Обработчик получения почтового индекса и перехода к вводу номера телефона
    """
    postal_code = message.text.strip()
    telegram_id = message.from_user.id

    # Валидация почтового индекса (6 цифр)
    if not re.match(r'^\d{6}$', postal_code):
        logger.warning(f"Пользователь {telegram_id} ввёл некорректный почтовый индекс: '{postal_code}'.")
        await message.answer("Почтовый индекс должен состоять из 6 цифр. Пожалуйста, введите почтовый индекс:")
        return

    await state.update_data(postal_code=postal_code)
    logger.info(f"Пользователь {telegram_id} ввёл почтовый индекс: {postal_code}")

    await message.answer("Введите номер телефона (+7XXXXXXXXXX или 8XXXXXXXXXX):")
    await state.set_state(OrderStates.waiting_for_phone_number)
    logger.info(f"Состояние пользователя {telegram_id} установлено на waiting_for_phone_number")


@router.message(OrderStates.waiting_for_phone_number, F.text)
async def process_phone_number(message: Message, state: FSMContext):
    """
    Обработчик получения номера телефона и создания заказа
    """
    phone_number = message.text.strip()
    telegram_id = message.from_user.id

    # Валидация номера телефона
    if not re.match(r'^(\+7|8)\d{10}$', phone_number):
        logger.warning(f"Пользователь {telegram_id} ввёл некорректный номер телефона: '{phone_number}'.")
        await message.answer("Введите корректный номер телефона в формате +7XXXXXXXXXX или 8XXXXXXXXXX:")
        return

    await state.update_data(phone_number=phone_number)
    logger.info(f"Пользователь {telegram_id} ввёл номер телефона: {phone_number}")

    user_data = await state.get_data()
    product_id = user_data.get('product_id')
    quantity = user_data.get('quantity')
    address = user_data.get('address')
    city = user_data.get('city')
    postal_code = user_data.get('postal_code')

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
        # Создание заказа через API с данными доставки
        order_response = await api_client.create_order(
            order_items=[
                {"product": product_id, "quantity": quantity}
            ],
            address=address,
            city=city,
            postal_code=postal_code,
            phone_number=phone_number
        )
        logger.debug(f"Ответ от API после создания заказа: {order_response}")

        # Проверка наличия 'id' в ответе
        if 'id' not in order_response:
            logger.error(f"Ответ API не содержит 'id': {order_response}")
            await message.answer("Произошла ошибка при создании заказа. Пожалуйста, попробуйте позже.")
            return

        # Сохраняем order_id в состоянии для дальнейшего подтверждения
        await state.update_data(order_id=order_response['id'])
        logger.info(f"Заказ №{order_response['id']} успешно создан для пользователя {telegram_id}.")

        await message.answer(
            f"Ваш заказ №{order_response['id']} успешно создан!",
            reply_markup=confirm_order_kb  # Добавляем клавиатуру с кнопками подтверждения
        )
        await state.set_state(OrderStates.active_order)  # Устанавливаем состояние активного заказа
        logger.info(f"Состояние пользователя {telegram_id} установлено на active_order")
    except Exception as e:
        logger.exception(f"Ошибка при создании заказа для пользователя {telegram_id}: {e}")
        await message.answer(f"Произошла ошибка при создании заказа: {str(e)}")
    finally:
        await api_client.close()
        logger.debug(f"APIClient для пользователя {telegram_id} закрыт")

    # Теперь состояние очищается только после подтверждения заказа
