# telegramadmin_bot/main.py

import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, Router
from telegramadmin_bot.config import ADMIN_BOT_TOKEN
from telegramadmin_bot.handlers import orders, analytics  # Импортируем обработчики

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flower_delivery.settings')
import django
django.setup()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('telegramadmin_bot')

# Инициализация бота и диспетчера
bot = Bot(token=ADMIN_BOT_TOKEN)
router = Router()  # Создаем основной маршрутизатор
dispatcher = Dispatcher()

# Подключаем маршрутизаторы из обработчиков
dispatcher.include_router(orders.router)
dispatcher.include_router(analytics.router)

# Асинхронная функция запуска бота
async def main():
    await dispatcher.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
