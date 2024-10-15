from dotenv import load_dotenv
import os

# Определение пути к .env файлу
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

# Доступ к переменным
API_URL = os.getenv('API_URL')
ADMIN_TELEGRAM_IDS = os.getenv('ADMIN_TELEGRAM_IDS').split(',')
BOT_TOKEN = os.getenv('BOT_TOKEN')

print(f"API_URL: {API_URL}")
print(f"ADMIN_TELEGRAM_IDS: {ADMIN_TELEGRAM_IDS}")
print(f"BOT_TOKEN: {BOT_TOKEN}")
