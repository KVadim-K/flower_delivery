# telegramadmin_bot/handlers/orders.py

from aiogram import Bot, Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from telegramadmin_bot.config import ADMIN_BOT_TOKEN, ADMIN_TELEGRAM_IDS
from orders.models import Order
from asgiref.sync import sync_to_async
import logging
import re

# Инициализация бота
bot = Bot(token=ADMIN_BOT_TOKEN)
logger = logging.getLogger('telegramadmin_bot')
router = Router()

async def is_admin(user_id):
    return user_id in ADMIN_TELEGRAM_IDS

async def notify_admins_of_new_order(order):
    # Получаем связанные товары асинхронно
    order_items = await sync_to_async(list)(order.order_items.all())
    items_list = "\n".join([
        f"- {await sync_to_async(lambda: item.product.name)()} x {item.quantity}"
        for item in order_items
    ])

    # Формируем текст уведомления
    message_text = (
        f"🆕 Новый заказ!\n\n"
        f"**ID:** {order.id}\n"
        f"**Пользователь:** {order.user.username}\n"
        f"**Сумма:** {order.total_price} ₽\n"
        f"**Товары:**\n{items_list}\n\n"
        f"**Статус:** {order.get_status_display()}"
    )

    # Создаем клавиатуру
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Детали заказа", callback_data=f"detail_{order.id}"),
            InlineKeyboardButton(text="Изменить статус", callback_data=f"change_{order.id}")
        ]
    ])

    # Отправляем сообщение всем администраторам
    for admin_id in ADMIN_TELEGRAM_IDS:
        try:
            await bot.send_message(admin_id, message_text, reply_markup=keyboard, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления администратору {admin_id}: {e}")

@router.message(Command(commands=['orders']))
async def list_orders(message: types.Message):
    if not await is_admin(message.from_user.id):
        await message.reply("У вас нет доступа к этому боту.")
        return

    orders = await sync_to_async(list)(Order.objects.all().order_by('-created_at')[:10])
    if not orders:
        await message.reply("Нет доступных заказов.")
        return

    for order in orders:
        username = await sync_to_async(lambda: order.user.username)()
        status_display = await sync_to_async(order.get_status_display)()
        created_at = await sync_to_async(order.created_at.strftime)('%Y-%m-%d %H:%M')

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Детали", callback_data=f"detail_{order.id}"),
                InlineKeyboardButton(text="Изменить статус", callback_data=f"change_{order.id}")
            ]
        ])

        await message.reply(
            f"ID: {order.id} | Пользователь: {username} | Статус: {status_display} | Дата: {created_at}",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )

@router.message(Command(commands=['order']))
async def order_details(message: types.Message):
    if not await is_admin(message.from_user.id):
        await message.reply("У вас нет доступа к этому боту.")
        return

    try:
        _, order_id_str = message.text.split()
        order_id = int(order_id_str)
        order = await sync_to_async(Order.objects.get)(id=order_id)
    except (ValueError, Order.DoesNotExist):
        await message.reply("Неверный формат команды или заказ не найден. Используйте: /order <id>")
        return

    username = await sync_to_async(lambda: order.user.username)()
    status_display = await sync_to_async(order.get_status_display)()
    created_at = await sync_to_async(order.created_at.strftime)('%Y-%m-%d %H:%M')

    response = (
        f"**Детали заказа ID: {order.id}**\n"
        f"**Пользователь:** {username}\n"
        f"**Статус:** {status_display}\n"
        f"**Дата:** {created_at}\n"
        f"**Адрес:** {order.address}, {order.city}, {order.postal_code}\n"
        f"**Телефон:** {order.phone_number}\n"
        f"**Сумма:** {order.total_price} ₽\n"
        f"**Товары:**\n"
    )

    order_items = await sync_to_async(list)(order.order_items.all())
    for item in order_items:
        product_name = await sync_to_async(lambda: item.product.name)()
        response += f"- {product_name} x {item.quantity} = {item.product.price * item.quantity} ₽\n"

    await message.reply(response, parse_mode='Markdown')

@router.callback_query(lambda call: call.data and (call.data.startswith('detail_') or call.data.startswith('change_')))
async def callback_handler(callback_query: types.CallbackQuery):
    if not await is_admin(callback_query.from_user.id):
        await callback_query.answer("У вас нет доступа к этому боту.", show_alert=True)
        return

    data = callback_query.data
    if data.startswith("detail_"):
        try:
            order_id = int(data.split('_')[1])
            order = await sync_to_async(Order.objects.get)(id=order_id)
        except (ValueError, Order.DoesNotExist):
            await callback_query.answer("Заказ не найден.", show_alert=True)
            return

        username = await sync_to_async(lambda: order.user.username)()
        status_display = await sync_to_async(order.get_status_display)()
        created_at = await sync_to_async(order.created_at.strftime)('%Y-%m-%d %H:%M')

        response = (
            f"**Детали заказа ID: {order.id}**\n"
            f"**Пользователь:** {username}\n"
            f"**Статус:** {status_display}\n"
            f"**Дата:** {created_at}\n"
            f"**Адрес:** {order.address}, {order.city}, {order.postal_code}\n"
            f"**Телефон:** {order.phone_number}\n"
            f"**Сумма:** {order.total_price} ₽\n"
            f"**Товары:**\n"
        )

        order_items = await sync_to_async(list)(order.order_items.all())
        for item in order_items:
            product_name = await sync_to_async(lambda: item.product.name)()
            response += f"- {product_name} x {item.quantity} = {item.product.price * item.quantity} ₽\n"

        await callback_query.message.reply(response, parse_mode='Markdown')

    elif data.startswith("change_"):
        try:
            order_id = int(data.split('_')[1])
            order = await sync_to_async(Order.objects.get)(id=order_id)
        except (ValueError, Order.DoesNotExist):
            await callback_query.answer("Заказ не найден.", show_alert=True)
            return

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=status_name,
                    callback_data=f"set_status_{order.id}_{status_code}"
                )
                for status_code, status_name in Order.STATUS_CHOICES if status_code != order.status
            ]
        ])

        await callback_query.message.reply(
            f"Выберите новый статус для заказа ID {order.id}:",
            reply_markup=keyboard
        )

@router.callback_query(lambda call: call.data and call.data.startswith('set_status_'))
async def set_status(callback_query: types.CallbackQuery):
    logger.info(f"Получено set_status callback_data: {repr(callback_query.data)}")

    if not await is_admin(callback_query.from_user.id):
        await callback_query.answer("У вас нет доступа к этому боту.", show_alert=True)
        return

    clean_data = callback_query.data.strip()
    match = re.match(r"^set_status_(\d+)_(\w+)$", clean_data)

    if not match:
        logger.error(f"Некорректный формат callback_data: {clean_data} (не соответствует шаблону)")
        await callback_query.answer("Неверный формат данных.", show_alert=True)
        return

    order_id_str, new_status = match.groups()

    if not order_id_str.isdigit():
        logger.error(f"Некорректный ID заказа: {order_id_str}")
        await callback_query.answer("Некорректный ID заказа.", show_alert=True)
        return

    order_id = int(order_id_str)

    try:
        order = await sync_to_async(Order.objects.get)(id=order_id)
    except Order.DoesNotExist:
        logger.error(f"Заказ с ID {order_id} не найден")
        await callback_query.answer("Заказ не найден.", show_alert=True)
        return

    if new_status not in dict(Order.STATUS_CHOICES).keys():
        logger.error(f"Неверный статус: {new_status}")
        await callback_query.answer("Неверный статус.", show_alert=True)
        return

    old_status_display = await sync_to_async(lambda: dict(Order.STATUS_CHOICES)[order.status])()
    new_status_display = await sync_to_async(lambda: dict(Order.STATUS_CHOICES)[new_status])()

    order.status = new_status
    await sync_to_async(order.save)()

    logger.info(f"Статус заказа ID {order.id} изменен с {old_status_display} на {new_status_display}")

    await callback_query.message.reply(
        f"Статус заказа ID {order.id} изменен с {old_status_display} на {new_status_display}.",
        parse_mode='Markdown'
    )
    await callback_query.answer("Статус изменен")
