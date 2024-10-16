import logging
from aiogram import BaseMiddleware
from aiogram.types import Message

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if isinstance(event, Message):
            logger.info(f"Получено сообщение от пользователя {event.from_user.id}: {event.text}")
        result = await handler(event, data)
        if isinstance(event, Message):
            logger.info(f"Сообщение обработано для пользователя {event.from_user.id}")
        return result
