# telegram_bot/bot/middlewares/logging_middleware.py

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
import logging

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if isinstance(event, Message):
            logger.info(f"Получено сообщение от пользователя {event.from_user.id}: {event.text}")
        elif isinstance(event, CallbackQuery):
            logger.info(f"Получен CallbackQuery от пользователя {event.from_user.id}: {event.data}")
        response = await handler(event, data)
        if isinstance(event, Message):
            logger.info(f"Отправлено сообщение пользователю {event.from_user.id}")
        elif isinstance(event, CallbackQuery):
            logger.info(f"Ответ на CallbackQuery для пользователя {event.from_user.id}")
        return response
