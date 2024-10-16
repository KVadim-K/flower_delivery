from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from telegram_bot.bot.keyboards.inline import navigation_kb, order_details_kb
from telegram_bot.bot.utils.api_client import APIClient, get_user_api_token

import os
from dotenv import load_dotenv
import aiohttp

load_dotenv()

router = Router()

@router.callback_query(F.data == "confirm_link")
async def confirm_link_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик подтверждения связывания аккаунта
    """
    user_data = await state.get_data()
    username = user_data.get('username')
    telegram_id = callback.from_user.id

    # Получение API-токена администратора для выполнения связывания
    admin_token = os.getenv("ADMIN_API_TOKEN")
    if not admin_token:
        await callback.message.answer("Связывание временно недоступно. Попробуйте позже.")
        await callback.answer()
        return

    api_client = APIClient(token=admin_token)

    try:
        link_response = await api_client.link_telegram_id(username, telegram_id)
        await callback.message.edit_text(
            f"Ваш Telegram аккаунт успешно связан с учётной записью '{username}'.",
            reply_markup=navigation_kb
        )
    except Exception as e:
        await callback.message.answer(f"Произошла ошибка при связывании: {str(e)}")
    finally:
        await api_client.close()

    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "cancel_link")
async def cancel_link_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик отмены связывания аккаунта
    """
    await callback.message.edit_text(
        "Связывание аккаунта отменено.",
        reply_markup=navigation_kb
    )
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "confirm_order")
async def confirm_order_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик подтверждения создания заказа
    """
    # Предполагается, что данные заказа уже сохранены в состоянии FSM
    user_data = await state.get_data()
    order_id = user_data.get('order_id')

    # Здесь можно добавить логику подтверждения заказа через API Django
    # Например, отправить запрос на подтверждение заказа

    await callback.message.edit_text(
        f"Ваш заказ №{order_id} подтверждён.",
        reply_markup=navigation_kb
    )
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "cancel_order")
async def cancel_order_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик отмены создания заказа
    """
    await callback.message.edit_text(
        "Создание заказа отменено.",
        reply_markup=navigation_kb
    )
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "create_order")
async def create_order_callback(callback: CallbackQuery):
    """
    Обработчик нажатия кнопки "Создать заказ"
    """
    await callback.message.edit_text(
        "Пожалуйста, введите название цветка, который вы хотите заказать:",
        reply_markup=InlineKeyboardMarkup()  # Убираем клавиатуру при вводе
    )
    await callback.answer()
    # Инициируем процесс создания заказа, переводя пользователя в соответствующее состояние
    await callback.message.answer("/order")

@router.callback_query(F.data == "view_orders")
async def view_orders_callback(callback: CallbackQuery):
    """
    Обработчик нажатия кнопки "Посмотреть заказы"
    """
    # Получаем API-токен пользователя по его Telegram ID
    user_api_token = await get_user_api_token(callback.from_user.id)
    if not user_api_token:
        await callback.message.answer("Ваш Telegram аккаунт не связан с учётной записью на сайте. Используйте /link для связывания.")
        await callback.answer()
        return

    api_client = APIClient(token=user_api_token)

    try:
        orders = await api_client.get_user_orders()
        if not orders:
            await callback.message.edit_text("У вас пока нет заказов.", reply_markup=navigation_kb)
        else:
            orders_text = "Ваши заказы:\n"
            for order in orders:
                orders_text += f"Заказ №{order['id']} - Статус: {order['status']}\n"
            await callback.message.edit_text(orders_text, reply_markup=navigation_kb)
    except Exception as e:
        await callback.message.answer(f"Произошла ошибка при получении заказов: {str(e)}")
    finally:
        await api_client.close()

    await callback.answer()

@router.callback_query(F.data == "help")
async def help_callback(callback: CallbackQuery):
    """
    Обработчик нажатия кнопки "Помощь"
    """
    help_text = (
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать это сообщение\n"
        "/link <username> - Связать Telegram аккаунт с учётной записью на сайте\n"
        "/order - Создать новый заказ\n"
        "/status <order_id> - Узнать статус заказа"
    )
    await callback.message.edit_text(help_text, reply_markup=navigation_kb)
    await callback.answer()

@router.callback_query(F.data == "back_to_orders")
async def back_to_orders_callback(callback: CallbackQuery):
    """
    Обработчик кнопки "Назад" в деталях заказа
    """
    await callback.message.edit_text("Ваши заказы:", reply_markup=navigation_kb)
    await callback.answer()
