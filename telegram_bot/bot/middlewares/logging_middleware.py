# telegram_bot/bot/middlewares/logging_middleware.py

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
import logging

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        logger.info(f"Получено событие: {event}")
        return await handler(event, data)

    async def on_pre_process_message(self, message: Message, data: dict, *args):
        logger.info(f"Получено сообщение от пользователя {message.from_user.id}: {message.text}")

    async def on_pre_process_callback_query(self, callback: CallbackQuery, data: dict, *args):
        logger.info(f"Получен callback от пользователя {callback.from_user.id}: {callback.data}")
