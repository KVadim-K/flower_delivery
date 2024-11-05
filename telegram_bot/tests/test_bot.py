from django.test import TestCase
from unittest.mock import AsyncMock, MagicMock, ANY
from telegram_bot.bot.handlers.commands import cmd_start
import asyncio
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext

class TestStartCommand(TestCase):
    def test_cmd_start(self):
        async def run_test():
            # Создаем mock message
            message = MagicMock()
            message.chat.id = 12345
            message.from_user.id = 12345
            message.from_user.full_name = 'Test User'  # Задаем полное имя пользователя
            message.text = '/start'
            message.answer = AsyncMock()

            # Создаем mock state
            storage = MemoryStorage()
            state = FSMContext(storage=storage, key=("user", 12345, "chat", 12345))

            # Вызываем обработчик
            await cmd_start(message, state)

            # Ожидаемое сообщение
            expected_text = (
                "Привет, Test User! Я бот FlowerDelivery.\n"
                "Используй кнопки ниже для взаимодействия."
            )

            # Проверяем, что message.answer был вызван с правильными аргументами
            message.answer.assert_called_once_with(
                expected_text,
                reply_markup=ANY,  # Игнорируем детали reply_markup
                parse_mode='HTML'
            )

        asyncio.run(run_test())
