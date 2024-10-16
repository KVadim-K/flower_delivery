from aiogram.fsm.state import StatesGroup, State

class OrderStates(StatesGroup):  #  Определяет состояния FSM для процесса создания заказа
    waiting_for_product = State()  #  Ожидает выбора продукта
    waiting_for_quantity = State()  #  Ожидает выбора количества
