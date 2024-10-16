from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Опционально: если вы хотите использовать стандартные клавиатуры
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
