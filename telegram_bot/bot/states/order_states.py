# telegram_bot/bot/states/order_states.py

from aiogram.fsm.state import StatesGroup, State

class OrderStates(StatesGroup):
    waiting_for_product_selection = State()
    waiting_for_quantity = State()
    adding_more_products = State()
    waiting_for_address = State()
    waiting_for_city = State()
    waiting_for_postal_code = State()
    waiting_for_phone_number = State()
    waiting_for_confirmation = State()
    active_order = State()  # Состояние для отслеживания активного заказа
    # Добавьте другие состояния, если необходимо
