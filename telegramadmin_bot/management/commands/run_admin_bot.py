# telegramadmin_bot/management/commands/run_admin_bot.py

from django.core.management.base import BaseCommand
import asyncio
from telegramadmin_bot.main import main as admin_bot_main
import logging

logger = logging.getLogger('telegramadmin_bot')

class Command(BaseCommand):
    help = 'Запускает административного Telegram-бота'

    def handle(self, *args, **options):
        logger.info("Запуск административного Telegram-бота...")
        try:
            asyncio.run(admin_bot_main())
        except KeyboardInterrupt:
            logger.info("Бот остановлен пользователем.")
        except Exception as e:
            logger.error(f"Ошибка при запуске бота: {e}")
