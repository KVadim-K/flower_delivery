# telegramadmin_bot/tasks.py

from celery import shared_task
from telegramadmin_bot.config import ADMIN_TELEGRAM_IDS, ADMIN_BOT_TOKEN
import logging
from aiogram import Bot, types
import asyncio

logger = logging.getLogger('telegramadmin_bot')

@shared_task
def send_notification_to_admins(order_id):
    """
    Асинхронная задача для отправки уведомления администраторам о новом заказе.
    """
    # Импортируем модель внутри функции, чтобы избежать циклических импортов
    from orders.models import Order

    try:
        # Получаем объект заказа с предзагруженным пользователем и товарами
        order = Order.objects.select_related("user").prefetch_related("order_items__product").get(id=order_id)
        order_items = list(order.order_items.all())
    except Order.DoesNotExist:
        logger.error(f"Заказ с ID {order_id} не найден.")
        return
    except Exception as e:
        logger.error(f"Ошибка при получении заказа с ID {order_id}: {e}")
        return

    try:
        username = order.user.username
        status_display = order.get_status_display()
        items_list = "\n".join([
            f"🌸 {item.product.name} x {item.quantity}" for item in order_items
        ])
    except Exception as e:
        logger.error(f"Ошибка при обработке данных заказа ID {order_id}: {e}")
        return

    # Формируем текст уведомления
    message_text = (
        f"🆕 **Новый заказ!**\n\n"
        f"🔢 **ID:** {order.id}\n"
        f"👤 **Пользователь:** {username}\n"
        f"💰 **Сумма:** {order.total_price} ₽\n"
        f"🛍️ **Товары:**\n{items_list}\n\n"
        f"📦 **Статус:** {status_display}"
    )

    # Создаем клавиатуру
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="📄 Детали заказа", callback_data=f"detail_{order.id}"),
            types.InlineKeyboardButton(text="🔄 Изменить статус", callback_data=f"change_{order.id}")
        ]
    ])

    # Функция для отправки сообщений администраторам
    async def send_messages():
        async with Bot(token=ADMIN_BOT_TOKEN) as bot:
            for admin_id in ADMIN_TELEGRAM_IDS:
                try:
                    await bot.send_message(
                        admin_id,
                        message_text,
                        reply_markup=keyboard,
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    logger.error(f"Ошибка при отправке уведомления администратору {admin_id}: {e}")

    # Запускаем асинхронную отправку сообщений
    asyncio.run(send_messages())

