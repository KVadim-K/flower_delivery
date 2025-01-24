# telegram_bot/bot/keyboards/default.py

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

order_button = KeyboardButton('/order')
status_button = KeyboardButton('/status')
help_button = KeyboardButton('/help')

default_kb = ReplyKeyboardMarkup(
    keyboard=[
        [order_button, status_button],
        [help_button]
    ],
    resize_keyboard=True
)
