# telegramadmin_bot/tasks.py

from celery import shared_task
from orders.models import Order
from telegramadmin_bot.config import ADMIN_TELEGRAM_IDS, ADMIN_BOT_TOKEN
import logging
from aiogram import Bot, types
import asyncio

logger = logging.getLogger('telegramadmin_bot')


@shared_task
def send_new_order_notification(order_id):
    async def notify_admins_of_new_order(order):
        # Получаем данные из базы данных и формируем сообщение
        user_username = await asyncio.to_thread(lambda: order.user.username)
        order_status = await asyncio.to_thread(order.get_status_display)
        created_at = await asyncio.to_thread(lambda: order.created_at.strftime('%Y-%m-%d %H:%M'))
        address, city, postal_code, phone_number, total_price = (
            order.address, order.city, order.postal_code, order.phone_number, order.total_price
        )

        # Формируем текст сообщения
        message = (
            f"📦 **Новый заказ ID: {order.id}**\n"
            f"👤 **Пользователь:** {user_username}\n"
            f"**Статус:** {order_status}\n"
            f"**Дата:** {created_at}\n"
            f"**Адрес:** {address}, {city}, {postal_code}\n"
            f"**Телефон:** {phone_number}\n"
            f"**Сумма:** {total_price} ₽\n"
            f"**Товары:**\n"
        )

        # Получаем товары в заказе и добавляем их в сообщение
        order_items = await asyncio.to_thread(lambda: list(order.order_items.all()))
        for item in order_items:
            product_name = await asyncio.to_thread(lambda: item.product.name)
            product_price = await asyncio.to_thread(lambda: item.product.price)
            message += f"- {product_name} x {item.quantity} = {product_price * item.quantity} ₽\n"

        # Отправляем сообщение каждому администратору с корректным закрытием бота
        async with Bot(token=ADMIN_BOT_TOKEN) as bot:
            detail_button = types.InlineKeyboardButton(text="Детали заказа", callback_data=f"detail_{order.id}")
            change_status_button = types.InlineKeyboardButton(text="Изменить статус", callback_data=f"change_{order.id}")
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[detail_button, change_status_button]])

            for admin_id in ADMIN_TELEGRAM_IDS:
                try:
                    await bot.send_message(
                        chat_id=admin_id,
                        text=message,
                        reply_markup=keyboard,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"Ошибка при отправке уведомления администратору {admin_id}: {e}")

    try:
        # Получаем заказ и запускаем асинхронную функцию уведомления
        order = Order.objects.prefetch_related('order_items__product').get(id=order_id)
        asyncio.run(notify_admins_of_new_order(order))
    except Order.DoesNotExist:
        logger.error(f"Заказ с ID {order_id} не найден.")
