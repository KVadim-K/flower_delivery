# telegramadmin_bot/handlers/orders.py

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from telegramadmin_bot.config import ADMIN_TELEGRAM_IDS
from asgiref.sync import sync_to_async
from orders.models import Order
import logging
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger('telegramadmin_bot')

router = Router()


async def is_admin(user_id):
    return user_id in ADMIN_TELEGRAM_IDS


@router.message(Command(commands=['orders']))
async def list_orders(message: types.Message):
    if not await is_admin(message.from_user.id):
        await message.reply("У вас нет доступа к этому боту.")
        return

    # Получаем заказы асинхронно
    orders = await sync_to_async(list)(Order.objects.all().order_by('-created_at')[:10])
    if not orders:
        await message.reply("Нет доступных заказов.")
        return

    for order in orders:
        # Оборачиваем доступ к полям модели в sync_to_async
        username = await sync_to_async(lambda: order.user.username)()
        status_display = await sync_to_async(order.get_status_display)()
        created_at = await sync_to_async(order.created_at.strftime)('%Y-%m-%d %H:%M')

        detail_button = InlineKeyboardButton(text="Детали", callback_data=f"detail_{order.id}")
        change_status_button = InlineKeyboardButton(text="Изменить статус", callback_data=f"change_{order.id}")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[detail_button, change_status_button]])

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
        _, order_id = message.text.split()
        order = await sync_to_async(Order.objects.get)(id=order_id)
    except (ValueError, ObjectDoesNotExist):
        await message.reply("Неверный формат команды или заказ не найден. Используйте: /order <id>")
        return

    # Оборачиваем доступ к полям модели в sync_to_async
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

    # Получаем элементы заказа асинхронно
    order_items = await sync_to_async(list)(order.order_items.all())
    for item in order_items:
        product_name = await sync_to_async(lambda: item.product.name)()
        product_price = await sync_to_async(lambda: item.product.price)()
        response += f"- {product_name} x {item.quantity} = {product_price * item.quantity} ₽\n"

    await message.reply(response, parse_mode='Markdown')


@router.message(Command(commands=['change_status']))
async def change_order_status(message: types.Message):
    if not await is_admin(message.from_user.id):
        await message.reply("У вас нет доступа к этому боту.")
        return

    try:
        _, order_id, new_status = message.text.split()
        order = await sync_to_async(Order.objects.get)(id=order_id)
        if new_status not in dict(Order.STATUS_CHOICES).keys():
            raise ValueError
    except (ValueError, ObjectDoesNotExist):
        await message.reply(
            "Неверный формат команды или заказ/статус не найден. Используйте: /change_status <id> <status>"
        )
        return

    old_status = order.status
    order.status = new_status
    await sync_to_async(order.save)()

    # Логирование изменения статуса
    old_status_display = await sync_to_async(lambda: dict(Order.STATUS_CHOICES)[old_status])()
    new_status_display = await sync_to_async(lambda: dict(Order.STATUS_CHOICES)[new_status])()
    logger.info(
        f"Order ID {order.id} status changed from {old_status} to {new_status} by user {message.from_user.id}"
    )

    await message.reply(
        f"Статус заказа ID {order.id} изменен с {old_status_display} на {new_status_display}.",
        parse_mode='Markdown'
    )