# telegram_bot/bot/states/order_states.py

from aiogram.fsm.state import StatesGroup, State

class OrderStates(StatesGroup):
    waiting_for_product_selection = State()
    waiting_for_quantity = State()
    confirming_order = State()
    active_order = State()  # Новое состояние для отслеживания активного заказа
    # Добавьте другие состояния, если необходимо


