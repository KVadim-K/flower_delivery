from aiogram.fsm.state import StatesGroup, State

class OrderStates(StatesGroup):
    waiting_for_product = State()
    waiting_for_quantity = State()
    confirming_order = State()
