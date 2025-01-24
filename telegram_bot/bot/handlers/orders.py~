from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from telegram_bot.bot.states.order_states import OrderStates
from telegram_bot.bot.utils.api_client import APIClient, get_user_api_token
from telegram_bot.bot.keyboards.inline import confirm_order_kb, navigation_kb
import logging
import os  # Для доступа к переменным окружения
import re  # Для валидации ввода

logger = logging.getLogger(__name__)

router = Router()

# Получаем API_URL из переменных окружения
API_URL = os.getenv('API_URL')
SITE_URL = os.getenv('SITE_URL')  # Для формирования ссылки на регистрацию

if not API_URL:
    logger.error("API_URL не установлен в переменных окружения")
    raise EnvironmentError("API_URL не установлен в переменных окружения")

if not SITE_URL:
    logger.error("SITE_URL не установлен в переменных окружения")
    raise EnvironmentError("SITE_URL не установлен в переменных окружения")


async def initiate_order_creation(source, state: FSMContext):
    """
    Общая функция для инициации создания заказа, вызываемая из команды /order и кнопки "Создать заказ"
    :param source: объект Message или CallbackQuery
    :param state: объект FSMContext
    """
    if isinstance(source, Message):
        send_message = source.answer
        user = source.from_user
    elif isinstance(source, CallbackQuery):
        send_message = source.message.edit_text
        user = source.from_user
    else:
        logger.error("Неизвестный тип источника для инициирования заказа")
        return

    telegram_id = user.id
    logger.debug(f"Инициация создания заказа для пользователя {telegram_id}")
    await send_message("🔄 Загрузка доступных товаров...")

    # Получение API-токена пользователя
    user_api_token = await get_user_api_token(telegram_id)
    if not user_api_token:
        logger.warning(f"Пользователь {telegram_id} не связан с учётной записью.")
        registration_link = f"{SITE_URL}/register/"
        await send_message(
            "🚫 Ваш Telegram аккаунт не связан с учётной записью на сайте.\n"
            f"Пожалуйста, зарегистрируйтесь на сайте: [Регистрация]({registration_link})\n"
            "После регистрации используйте команду /link для связывания аккаунтов.",
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        return

    # Проверка наличия активного заказа
    current_state = await state.get_state()
    if current_state and current_state not in [
        OrderStates.waiting_for_product_selection.state,
        OrderStates.waiting_for_quantity.state,
        OrderStates.adding_more_products.state,
    ]:
        logger.info(f"Пользователь {telegram_id} пытается создать новый заказ, но уже есть активный заказ.")
        await send_message(
            "⚠️ У вас уже есть активный процесс оформления заказа. Пожалуйста, завершите его или отмените перед созданием нового."
        )
        return

    api_client = APIClient(token=user_api_token)
    logger.debug(f"APIClient инициализирован для пользователя {telegram_id}")

    try:
        # Получение списка продуктов через API
        products = await api_client.get_products()
        logger.debug(f"Получен список продуктов: {products}")
        if not products:
            logger.info(f"У пользователя {telegram_id} нет доступных товаров.")
            await send_message("📦 На данный момент нет доступных товаров для заказа.")
            return

        # Сохраняем список продуктов в состояние
        await state.update_data(products=products)

        # Создание инлайн-клавиатуры с товарами
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"{product['name']} - {product['price']}₽",
                        callback_data=f"select_product:{product['id']}"
                    )
                ]
                for product in products
            ] + [[
                InlineKeyboardButton(
                    text="🛒 Перейти к оформлению заказа",
                    callback_data="proceed_to_checkout"
                )
            ]],
            row_width=1
        )

        logger.debug(f"Инлайн-клавиатура с продуктами создана для пользователя {telegram_id}")
        await send_message("🛍️ Пожалуйста, выберите товар из списка ниже:", reply_markup=keyboard)
        await state.set_state(OrderStates.waiting_for_product_selection)
        logger.info(f"Состояние пользователя {telegram_id} установлено на waiting_for_product_selection")
    except Exception as e:
        logger.exception(f"Ошибка при получении товаров для пользователя {telegram_id}: {e}")
        await send_message("⚠️ Произошла ошибка при получении списка товаров. Пожалуйста, попробуйте позже.")
    finally:
        await api_client.close()
        logger.debug(f"APIClient для пользователя {telegram_id} закрыт")


@router.message(Command(commands=["order"]))
async def cmd_order(message: Message, state: FSMContext):
    """
    Обработчик команды /order — инициирует процесс создания заказа
    """
    await initiate_order_creation(message, state)


@router.callback_query(F.data.startswith("select_product:"))
async def select_product_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора продукта из инлайн-клавиатуры
    """
    telegram_id = callback.from_user.id
    product_id = callback.data.split(":")[1]
    logger.info(f"Пользователь {telegram_id} выбрал продукт с ID {product_id}.")

    # Получаем информацию о продукте
    user_data = await state.get_data()
    products = user_data.get('products', [])
    product = next((p for p in products if str(p['id']) == product_id), None)
    if not product:
        await callback.answer("❌ Продукт не найден.", show_alert=True)
        return

    await state.update_data(selected_product=product)
    await state.set_state(OrderStates.waiting_for_quantity)

    await callback.message.edit_text(f"📦 Вы выбрали: {product['name']}.\n\nПожалуйста, введите количество:")
    await callback.answer()


@router.message(OrderStates.waiting_for_quantity, F.text)
async def process_quantity(message: Message, state: FSMContext):
    """
    Обработчик получения количества продукта и предложения добавить еще товары или перейти к оформлению
    """
    quantity_text = message.text.strip()
    telegram_id = message.from_user.id

    if not quantity_text.isdigit() or int(quantity_text) <= 0:
        logger.warning(f"Пользователь {telegram_id} ввёл некорректное количество: '{quantity_text}'.")
        await message.answer("❗ Пожалуйста, введите корректное количество (целое число, большее 0):")
        return

    quantity = int(quantity_text)
    user_data = await state.get_data()
    product = user_data.get('selected_product')

    if not product:
        logger.error(f"Продукт не найден в состоянии для пользователя {telegram_id}.")
        await message.answer("⚠️ Произошла ошибка. Попробуйте начать заново.")
        await state.clear()
        return

    # **Исправление:** Преобразуем цену продукта в число
    try:
        price = float(product['price'])
    except ValueError:
        logger.error(f"Не удалось преобразовать цену продукта в число: {product['price']}")
        await message.answer("⚠️ Произошла ошибка с ценой продукта. Пожалуйста, попробуйте позже.")
        await state.clear()
        return

    # Добавляем товар в корзину (список выбранных товаров в состоянии)
    cart = user_data.get('cart', [])
    cart.append({
        'product_id': product['id'],
        'product_name': product['name'],
        'quantity': quantity,
        'price': price  # Сохраняем цену как число
    })
    await state.update_data(cart=cart)
    logger.info(f"Пользователь {telegram_id} добавил '{quantity}' единиц продукта '{product['name']}' в корзину.")

    # Спрашиваем, хочет ли пользователь добавить еще товары или перейти к оформлению
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Добавить еще товар",
                    callback_data="add_more_products"
                ),
                InlineKeyboardButton(
                    text="🛒 Оформить заказ",
                    callback_data="proceed_to_checkout"
                )
            ]
        ],
        row_width=2
    )

    await message.answer("Хотите добавить еще товары или перейти к оформлению заказа?", reply_markup=keyboard)
    await state.set_state(OrderStates.adding_more_products)
    logger.info(f"Состояние пользователя {telegram_id} установлено на adding_more_products")


@router.callback_query(F.data == "add_more_products")
async def add_more_products_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик добавления еще товаров
    """
    telegram_id = callback.from_user.id
    logger.info(f"Пользователь {telegram_id} решил добавить еще товаров.")

    user_data = await state.get_data()
    products = user_data.get('products', [])

    # Создание инлайн-клавиатуры с товарами
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{product['name']} - {product['price']}₽",
                    callback_data=f"select_product:{product['id']}"
                )
            ]
            for product in products
        ] + [[
            InlineKeyboardButton(
                text="🛒 Перейти к оформлению заказа",
                callback_data="proceed_to_checkout"
            )
        ]],
        row_width=1
    )

    await callback.message.edit_text("🛍️ Пожалуйста, выберите товар из списка ниже:", reply_markup=keyboard)
    await state.set_state(OrderStates.waiting_for_product_selection)
    logger.info(f"Состояние пользователя {telegram_id} установлено на waiting_for_product_selection")
    await callback.answer()


@router.callback_query(F.data == "proceed_to_checkout")
async def proceed_to_checkout_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик перехода к оформлению заказа
    """
    telegram_id = callback.from_user.id
    logger.info(f"Пользователь {telegram_id} переходит к оформлению заказа.")

    user_data = await state.get_data()
    cart = user_data.get('cart', [])

    if not cart:
        await callback.answer("❗ Ваша корзина пуста. Пожалуйста, добавьте товары.", show_alert=True)
        return

    # Формируем текст с содержимым корзины
    cart_text = "🛒 <b>Ваш заказ:</b>\n\n"
    total_price = 0
    for item in cart:
        # **Исправление:** Убеждаемся, что цена и количество - числа
        try:
            item_price = float(item['price'])
            item_quantity = int(item['quantity'])
            item_total = item_price * item_quantity
            total_price += item_total
            cart_text += f"🌸 {item['product_name']} x {item_quantity} = {item_total:.2f}₽\n"
        except ValueError as e:
            logger.error(f"Ошибка при расчете стоимости товара: {e}")
            await callback.message.edit_text("⚠️ Произошла ошибка при расчете стоимости заказа. Пожалуйста, попробуйте позже.")
            await state.clear()
            return

    cart_text += f"\n💰 <b>Общая стоимость: {total_price:.2f}₽</b>\n\n"
    cart_text += "📍 Пожалуйста, введите адрес доставки:"

    await callback.message.edit_text(cart_text, parse_mode='HTML')
    await state.update_data(total_price=total_price)
    await state.set_state(OrderStates.waiting_for_address)
    logger.info(f"Состояние пользователя {telegram_id} установлено на waiting_for_address")
    await callback.answer()


@router.message(OrderStates.waiting_for_address, F.text)
async def process_address(message: Message, state: FSMContext):
    """
    Обработчик получения адреса доставки и перехода к вводу города
    """
    address = message.text.strip()
    telegram_id = message.from_user.id

    # Простая валидация адреса
    if len(address.split()) < 2:
        logger.warning(f"Пользователь {telegram_id} ввёл некорректный адрес: '{address}'.")
        await message.answer("❗ Пожалуйста, укажите полный адрес, включая улицу и номер дома:")
        return

    await state.update_data(address=address)
    logger.info(f"Пользователь {telegram_id} ввёл адрес доставки: {address}")

    await message.answer("🏙️ Пожалуйста, введите город:")
    await state.set_state(OrderStates.waiting_for_city)
    logger.info(f"Состояние пользователя {telegram_id} установлено на waiting_for_city")


@router.message(OrderStates.waiting_for_city, F.text)
async def process_city(message: Message, state: FSMContext):
    """
    Обработчик получения города и перехода к вводу почтового индекса
    """
    city = message.text.strip()
    telegram_id = message.from_user.id

    # Валидация города (только буквы, пробелы, дефисы)
    if not re.match(r'^[A-Za-zА-Яа-яЁё\s-]+$', city):
        logger.warning(f"Пользователь {telegram_id} ввёл некорректный город: '{city}'.")
        await message.answer("❗ Город может содержать только буквы, пробелы и дефисы. Пожалуйста, введите город:")
        return

    await state.update_data(city=city)
    logger.info(f"Пользователь {telegram_id} ввёл город: {city}")

    await message.answer("📮 Пожалуйста, введите почтовый индекс (6 цифр):")
    await state.set_state(OrderStates.waiting_for_postal_code)
    logger.info(f"Состояние пользователя {telegram_id} установлено на waiting_for_postal_code")


@router.message(OrderStates.waiting_for_postal_code, F.text)
async def process_postal_code(message: Message, state: FSMContext):
    """
    Обработчик получения почтового индекса и перехода к вводу номера телефона
    """
    postal_code = message.text.strip()
    telegram_id = message.from_user.id

    # Валидация почтового индекса (6 цифр)
    if not re.match(r'^\d{6}$', postal_code):
        logger.warning(f"Пользователь {telegram_id} ввёл некорректный почтовый индекс: '{postal_code}'.")
        await message.answer("❗ Почтовый индекс должен состоять из 6 цифр. Пожалуйста, введите почтовый индекс:")
        return

    await state.update_data(postal_code=postal_code)
    logger.info(f"Пользователь {telegram_id} ввёл почтовый индекс: {postal_code}")

    await message.answer("📱 Пожалуйста, введите номер телефона (+7XXXXXXXXXX или 8XXXXXXXXXX):")
    await state.set_state(OrderStates.waiting_for_phone_number)
    logger.info(f"Состояние пользователя {telegram_id} установлено на waiting_for_phone_number")


@router.message(OrderStates.waiting_for_phone_number, F.text)
async def process_phone_number(message: Message, state: FSMContext):
    """
    Обработчик получения номера телефона и перехода к подтверждению заказа
    """
    phone_number = message.text.strip()
    telegram_id = message.from_user.id

    # Валидация номера телефона
    if not re.match(r'^(\+7|8)\d{10}$', phone_number):
        logger.warning(f"Пользователь {telegram_id} ввёл некорректный номер телефона: '{phone_number}'.")
        await message.answer("❗ Введите корректный номер телефона в формате +7XXXXXXXXXX или 8XXXXXXXXXX:")
        return

    await state.update_data(phone_number=phone_number)
    logger.info(f"Пользователь {telegram_id} ввёл номер телефона: {phone_number}")

    user_data = await state.get_data()
    cart = user_data.get('cart', [])
    address = user_data.get('address')
    city = user_data.get('city')
    postal_code = user_data.get('postal_code')
    total_price = user_data.get('total_price', 0)

    # Формируем текст заказа для подтверждения
    order_summary = "📋 **Пожалуйста, подтвердите ваш заказ:**\n\n"
    for item in cart:
        item_total = item['price'] * item['quantity']
        order_summary += f"🌸 {item['product_name']} x {item['quantity']} = {item_total:.2f}₽\n"
    order_summary += f"\n💰 **Общая стоимость:** {total_price:.2f}₽\n"
    order_summary += f"\n📍 **Адрес доставки:** {address}, {city}, {postal_code}\n"
    order_summary += f"📱 **Телефон:** {phone_number}\n"

    await message.answer(order_summary, reply_markup=confirm_order_kb, parse_mode='Markdown')
    await state.set_state(OrderStates.waiting_for_confirmation)
    logger.info(f"Состояние пользователя {telegram_id} установлено на waiting_for_confirmation")


@router.callback_query(F.data == "confirm_order")
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик подтверждения заказа
    """
    telegram_id = callback.from_user.id
    user_data = await state.get_data()

    cart = user_data.get('cart', [])
    address = user_data.get('address')
    city = user_data.get('city')
    postal_code = user_data.get('postal_code')
    phone_number = user_data.get('phone_number')

    # Получение API-токена пользователя
    user_api_token = await get_user_api_token(telegram_id)
    if not user_api_token:
        logger.warning(f"Пользователь {telegram_id} не связан с учётной записью.")
        await callback.message.edit_text("🚫 Ваш Telegram аккаунт не связан с учётной записью на сайте. Используйте /link для связывания.")
        await state.clear()
        return

    api_client = APIClient(token=user_api_token)
    logger.debug(f"APIClient инициализирован для пользователя {telegram_id}")

    try:
        # Формируем список товаров для отправки в API
        order_items = [
            {"product": item['product_id'], "quantity": item['quantity']}
            for item in cart
        ]

        # Создание заказа через API с данными доставки
        order_response = await api_client.create_order(
            order_items=order_items,
            address=address,
            city=city,
            postal_code=postal_code,
            phone_number=phone_number
        )
        logger.debug(f"Ответ от API после создания заказа: {order_response}")

        # Проверка наличия 'id' в ответе
        if 'id' not in order_response:
            logger.error(f"Ответ API не содержит 'id': {order_response}")
            await callback.message.edit_text("⚠️ Произошла ошибка при создании заказа. Пожалуйста, попробуйте позже.")
            return

        order_id = order_response['id']
        logger.info(f"Заказ №{order_id} успешно создан для пользователя {telegram_id}.")

        await callback.message.edit_text(f"✅ Ваш заказ №{order_id} успешно создан!")
        await state.clear()
        await callback.answer()
    except Exception as e:
        logger.exception(f"Ошибка при создании заказа для пользователя {telegram_id}: {e}")
        await callback.message.edit_text(f"⚠️ Произошла ошибка при создании заказа: {str(e)}")
    finally:
        await api_client.close()
        logger.debug(f"APIClient для пользователя {telegram_id} закрыт")


@router.callback_query(F.data == "cancel_order")
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик отмены заказа
    """
    telegram_id = callback.from_user.id
    logger.info(f"Пользователь {telegram_id} отменил заказ.")
    await state.clear()
    await callback.message.edit_text("❌ Вы отменили оформление заказа.")
    await callback.answer()


# Обработчик для кнопки "Создать заказ" из навигационной клавиатуры
@router.callback_query(F.data == "create_order")
async def create_order_callback(callback: CallbackQuery, state: FSMContext):
    await initiate_order_creation(callback, state)
    await callback.answer()
