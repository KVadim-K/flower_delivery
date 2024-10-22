# telegram_bot/bot/handlers/commands.py

from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from telegram_bot.bot.keyboards.inline import navigation_kb, confirm_link_kb
from telegram_bot.bot.utils.api_client import APIClient

from aiogram.fsm.context import FSMContext

import logging

logger = logging.getLogger(__name__)

router = Router()

@router.message(Command(commands=["start"]))
async def cmd_start_handler(message: Message):
    """
    Обработчик команды /start
    """
    logger.info(f"Обработчик /start вызван пользователем {message.from_user.id}")
    await message.answer(
        f"Привет, {message.from_user.full_name}! Я бот FlowerDelivery.\n"
        "Используй кнопки ниже для взаимодействия.",
        reply_markup=navigation_kb,
        parse_mode="HTML"  # Убедитесь, что parse_mode установлен
    )

@router.message(Command(commands=["help"]))
async def cmd_help_handler(message: Message):
    """
    Обработчик команды /help
    """
    logger.info(f"Обработчик /help вызван пользователем {message.from_user.id}")
    await message.answer(
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать это сообщение\n"
        "/link &lt;username&gt; - Связать Telegram аккаунт с учётной записью на сайте\n"
        "/order - Создать новый заказ\n"
        "/status &lt;order_id&gt; - Узнать статус заказа",
        parse_mode="HTML"  # Явно указываем parse_mode
    )

@router.message(Command(commands=["link"]))
async def cmd_link_handler(message: Message, command: CommandObject, state: FSMContext):
    """
    Обработчик команды /link для связывания Telegram ID с пользователем Django
    """
    logger.info(f"Обработчик /link вызван пользователем {message.from_user.id} с аргументами: {command.args}")
    args = command.args
    if not args:
        await message.answer("Пожалуйста, укажите ваше имя пользователя на сайте. Пример: /link john_doe")
        return
    username = args.strip()

    # Отправляем сообщение с подтверждением связывания
    await message.answer(
        f"Вы хотите связать Telegram аккаунт с учётной записью '{username}'?",
        reply_markup=confirm_link_kb
    )

    # Сохраняем данные в состоянии FSM
    await state.update_data(username=username)
    await state.set_state("confirming_link")
