# telegramadmin_bot/main.py

import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from telegramadmin_bot.config import ADMIN_BOT_TOKEN, ADMIN_TELEGRAM_IDS
from telegramadmin_bot.handlers import orders, analytics  # Импортируем обработчики

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flower_delivery.settings')
import django
django.setup()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('telegramadmin_bot')

# Инициализация бота и маршрутизатора
bot = Bot(token=ADMIN_BOT_TOKEN)
router = Router()  # Создаем основной маршрутизатор

# Обработчик команды /start
@router.message(Command(commands=['start']))
async def send_welcome(message: types.Message):
    if message.from_user.id not in ADMIN_TELEGRAM_IDS:
        await message.reply("🚫 **У вас нет доступа к этому боту.**")
        return
    await message.reply(
        "Добро пожаловать в **Telegramadmin_bot** FlowerDelivery!\n\n"
        "Используйте следующие команды для управления заказами:\n"
        "/orders - Список заказов\n"
        "/order <id> - Детали заказа\n"
        "/change_status <id> <status> - Изменить статус заказа\n"
        "/analytics - Аналитика по заказам",
        parse_mode='Markdown'
    )

# Инициализация диспетчера
dispatcher = Dispatcher()

# Подключаем маршрутизаторы из обработчиков
dispatcher.include_router(router)          # Включаем основной маршрутизатор с /start
dispatcher.include_router(orders.router)   # Включаем роутер для заказов
dispatcher.include_router(analytics.router) # Включаем роутер для аналитики

# Асинхронная функция запуска бота
async def main():
    # Удалено логирование отсюда
    await dispatcher.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
