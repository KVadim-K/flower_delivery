# telegram_bot/bot/keyboards/inline.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Клавиатура для подтверждения заказа
confirm_order_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Подтвердить", callback_data="confirm_order"),
            InlineKeyboardButton(text="Отменить", callback_data="cancel_order")
        ]
    ]
)

# Клавиатура для просмотра деталей заказа
order_details_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Назад", callback_data="back_to_orders")
        ]
    ]
)

# Общая клавиатура с кнопками навигации
navigation_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Создать заказ", callback_data="create_order"),
            InlineKeyboardButton(text="Посмотреть заказы", callback_data="view_orders")
        ],
        [
            InlineKeyboardButton(text="Помощь", callback_data="help")
        ]
    ]
)

# Клавиатура для подтверждения связывания аккаунта
confirm_link_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Связать", callback_data="confirm_link"),
            InlineKeyboardButton(text="Отмена", callback_data="cancel_link")
        ]
    ]
)
