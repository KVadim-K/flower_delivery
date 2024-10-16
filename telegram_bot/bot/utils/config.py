import os
from dotenv import load_dotenv
import logging

# Определение пути к .env файлу
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env')  # Настройте путь согласно структуре вашего проекта
load_dotenv(dotenv_path=env_path)

# Доступ к переменным
API_URL = os.getenv('API_URL')
ADMIN_TELEGRAM_IDS = os.getenv('ADMIN_TELEGRAM_IDS', '').split(',')
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_API_TOKEN = os.getenv('ADMIN_API_TOKEN')  # Добавьте, если необходимо

if not BOT_TOKEN:
    logging.error("BOT_TOKEN не установлен в переменных окружения")
    sys.exit("BOT_TOKEN не установлен в переменных окружения")

# Другие переменные окружения могут быть добавлены здесь по мере необходимости
