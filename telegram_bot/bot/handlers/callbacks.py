# telegram_bot/bot/handlers/callbacks.py

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton  # Добавлены InlineKeyboardMarkup и InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from telegram_bot.bot.keyboards.inline import navigation_kb, confirm_order_kb
from telegram_bot.bot.utils.api_client import APIClient, get_user_api_token
from telegram_bot.bot.handlers.orders import initiate_order_creation  # Импортируем функцию

import logging
import os  # Для доступа к переменным окружения
import html  # Для экранирования

logger = logging.getLogger(__name__)

router = Router()

# Получаем ADMIN_API_TOKEN из переменных окружения
ADMIN_API_TOKEN = os.getenv('ADMIN_API_TOKEN')

if not ADMIN_API_TOKEN:
    logger.error("ADMIN_API_TOKEN не установлен в переменных окружения.")


@router.callback_query(F.data == "confirm_link")
async def confirm_link_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик подтверждения связывания аккаунта
    """
    user_data = await state.get_data()
    username = user_data.get('username')
    telegram_id = callback.from_user.id

    logger.info(f"Пользователь {telegram_id} подтверждает связывание с username '{username}'.")

    # Проверка наличия ADMIN_API_TOKEN
    if not ADMIN_API_TOKEN:
        logger.error("ADMIN_API_TOKEN не установлен в переменных окружения.")
        await callback.message.answer(
            "Связывание временно недоступно. Попробуйте позже.",
            reply_markup=navigation_kb,
            parse_mode="HTML"  # Добавили parse_mode
        )
        await callback.answer()
        return

    api_client = APIClient(token=ADMIN_API_TOKEN)

    try:
        await api_client.link_telegram_id(username, telegram_id)
        logger.info(f"Связывание аккаунта для username '{username}' прошло успешно.")
        safe_username = html.escape(username)
        welcome_message = (
            f"Ваш Telegram аккаунт успешно связан с учётной записью '{safe_username}'.\n"
            f"Привет, {callback.from_user.full_name}! Я бот FlowerDelivery.\n"
            "Используй кнопки ниже для взаимодействия."
        )
        await callback.message.edit_text(
            welcome_message,
            reply_markup=navigation_kb,  # Используем корректно импортированную клавиатуру
            parse_mode="HTML"  # Добавили parse_mode
        )
    except Exception as e:
        logger.error(f"Ошибка при связывании аккаунта: {e}")
        await callback.message.answer(
            "Произошла ошибка при связывании. Пожалуйста, попробуйте позже.",
            reply_markup=navigation_kb,
            parse_mode="HTML"  # Добавили parse_mode
        )
    finally:
        await api_client.close()

    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "cancel_link")
async def cancel_link_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик отмены связывания аккаунта
    """
    logger.info(f"Пользователь {callback.from_user.id} отменил связывание аккаунта.")
    await callback.message.edit_text(
        "Связывание аккаунта отменено.",
        reply_markup=navigation_kb,  # Используем корректно импортированную клавиатуру
        parse_mode="HTML"  # Добавили parse_mode
    )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "confirm_order")
async def confirm_order_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик подтверждения создания заказа
    """
    user_data = await state.get_data()
    order_id = user_data.get('order_id')
    telegram_id = callback.from_user.id

    logger.info(f"Пользователь {telegram_id} подтверждает заказ №{order_id}.")

    if not order_id:
        logger.error(f"Не удалось получить order_id для пользователя {telegram_id}.")
        await callback.message.edit_text(
            "Произошла ошибка при подтверждении заказа. Пожалуйста, попробуйте позже.",
            reply_markup=navigation_kb,
            parse_mode="HTML"  # Добавили parse_mode
        )
        await callback.answer()
        return

    # Здесь можно добавить логику подтверждения заказа через API Django
    # Например, отправить запрос на подтверждение заказа или обновление статуса

    await callback.message.edit_text(
        f"Ваш заказ №{order_id} подтверждён.",
        reply_markup=navigation_kb,  # Используем корректно импортированную клавиатуру
        parse_mode="HTML"  # Добавили parse_mode
    )
    await state.clear()  # Очищаем состояние после подтверждения
    logger.info(f"Состояние пользователя {telegram_id} очищено после подтверждения заказа")
    await callback.answer()


@router.callback_query(F.data == "cancel_order")
async def cancel_order_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик отмены создания заказа
    """
    user_data = await state.get_data()
    order_id = user_data.get('order_id')
    telegram_id = callback.from_user.id

    logger.info(f"Пользователь {telegram_id} отменил заказ №{order_id}.")

    await callback.message.edit_text(
        "Создание заказа отменено.",
        reply_markup=navigation_kb,  # Используем корректно импортированную клавиатуру
        parse_mode="HTML"  # Добавили parse_mode
    )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "create_order")
async def create_order_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик нажатия кнопки "Создать заказ"
    """
    telegram_id = callback.from_user.id
    logger.info(f"Пользователь {telegram_id} инициирует создание заказа через кнопку.")
    await initiate_order_creation(callback, state)  # Вызов функции создания заказа
    await callback.answer()


@router.callback_query(F.data == "view_orders")
async def view_orders_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик нажатия кнопки "Посмотреть заказы"
    """
    telegram_id = callback.from_user.id
    logger.info(f"Пользователь {telegram_id} запросил свои заказы.")

    # Получаем API-токен пользователя по его Telegram ID
    user_api_token = await get_user_api_token(telegram_id)
    if not user_api_token:
        logger.warning(f"Пользователь {telegram_id} не связан с учётной записью.")
        await callback.message.edit_text(
            "Ваш Telegram аккаунт не связан с учётной записью на сайте. Используйте /link для связывания.",
            reply_markup=navigation_kb,
            parse_mode="HTML"  # Добавили parse_mode
        )
        await callback.answer()
        return

    api_client = APIClient(token=user_api_token)

    try:
        orders = await api_client.get_user_orders()
        if not orders:
            logger.info(f"Пользователь {telegram_id} не имеет заказов.")
            await callback.message.edit_text(
                "У вас пока нет заказов.",
                reply_markup=navigation_kb,
                parse_mode="HTML"  # Добавили parse_mode
            )
        else:
            orders_text = "Ваши заказы:\n"
            for order in orders:
                status_display = order.get('status_display', 'Неизвестен')
                orders_text += f"Заказ №{order['id']} - Статус: {status_display}\n"
            logger.info(f"Заказы для пользователя {telegram_id}: {orders}")
            await callback.message.edit_text(
                orders_text,
                reply_markup=navigation_kb,
                parse_mode="HTML"  # Добавили parse_mode
            )
    except Exception as e:
        logger.error(f"Ошибка при получении заказов для пользователя {telegram_id}: {e}")
        # Не отправляем сырые исключения пользователю
        await callback.message.edit_text(
            "Произошла ошибка при получении заказов. Пожалуйста, попробуйте позже.",
            reply_markup=navigation_kb,
            parse_mode="HTML"  # Добавили parse_mode
        )
    finally:
        await api_client.close()

    await callback.answer()


@router.callback_query(F.data == "help")
async def help_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик нажатия кнопки "Помощь"
    """
    help_text = (
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать это сообщение\n"
        "/link <code>&lt;username&gt;</code> - Связать Telegram аккаунт с учётной записью на сайте\n"
        "/order - Создать новый заказ\n"
        "/status <code>&lt;order_id&gt;</code> - Узнать статус заказа"
    )
    telegram_id = callback.from_user.id
    logger.info(f"Пользователь {telegram_id} запросил помощь.")
    await callback.message.edit_text(
        help_text,
        reply_markup=navigation_kb,
        parse_mode="HTML"  # Добавили parse_mode
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_orders")
async def back_to_orders_callback(callback: CallbackQuery):
    """
    Обработчик кнопки "Назад" в деталях заказа
    """
    telegram_id = callback.from_user.id
    logger.info(f"Пользователь {telegram_id} вернулся к списку заказов.")
    await callback.message.edit_text(
        "Ваши заказы:",
        reply_markup=navigation_kb,
        parse_mode="HTML"  # Добавили parse_mode
    )
    await callback.answer()
