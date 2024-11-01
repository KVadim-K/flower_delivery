# telegramadmin_bot/handlers/analytics.py

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from telegramadmin_bot.config import ADMIN_TELEGRAM_IDS
from asgiref.sync import sync_to_async
from orders.models import Order
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Count
import logging

logger = logging.getLogger('telegramadmin_bot')

router = Router()

async def is_admin(user_id):
    return user_id in ADMIN_TELEGRAM_IDS

@router.message(Command(commands=['analytics']))
async def order_analytics(message: types.Message):
    if not await is_admin(message.from_user.id):
        await message.reply("У вас нет доступа к этому боту.")
        return

    total_orders = await sync_to_async(Order.objects.count)()
    total_sales = (await sync_to_async(Order.objects.aggregate)(total_sales=Sum('total_price')))['total_sales'] or 0
    orders_per_status = await sync_to_async(list)(Order.objects.values('status').annotate(count=Count('id')))

    response = (
        f"📊 **Аналитика по заказам** 📊\n\n"
        f"**Всего заказов:** {total_orders}\n"
        f"**Общая сумма продаж:** {total_sales} ₽\n\n"
        f"**Заказы по статусам:**\n"
    )
    for status_item in orders_per_status:
        status_display = dict(Order.STATUS_CHOICES).get(status_item['status'], status_item['status'])
        response += f"- {status_display}: {status_item['count']}\n"

    await message.reply(response, parse_mode='Markdown')
