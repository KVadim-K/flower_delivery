import logging
import os
import sys
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

# Добавление корневой директории проекта в sys.path для корректных импортов
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Определение пути к .env файлу
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

# Доступ к переменным
API_URL = os.getenv('API_URL')
ADMIN_TELEGRAM_IDS = os.getenv('ADMIN_TELEGRAM_IDS').split(',')
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    logging.error("BOT_TOKEN не установлен в переменных окружения")
    sys.exit("BOT_TOKEN не установлен в переменных окружения")

print(f"API_URL: {API_URL}")
print(f"ADMIN_TELEGRAM_IDS: {ADMIN_TELEGRAM_IDS}")
print(f"BOT_TOKEN: {BOT_TOKEN}")

# Импорт роутеров и middleware
from telegram_bot.bot.handlers.commands import router as commands_router
from telegram_bot.bot.handlers.orders import router as orders_router
from telegram_bot.bot.handlers.callbacks import router as callbacks_router  # Импортируйте роутер для callback
from telegram_bot.bot.middlewares.logging_middleware import LoggingMiddleware

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def main():
    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Регистрация middleware
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())  # Добавляем middleware для callback

    # Регистрация роутеров
    dp.include_router(commands_router)
    dp.include_router(orders_router)
    dp.include_router(callbacks_router)  # Подключение роутера callback

    try:
        logger.info("Запуск бота...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
