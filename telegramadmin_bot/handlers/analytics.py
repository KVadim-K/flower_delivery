from aiogram import Router, types
from aiogram.filters import Command
from telegramadmin_bot.config import ADMIN_TELEGRAM_IDS
from asgiref.sync import sync_to_async
from orders.models import Order
from django.db.models import Sum, Count, F, ExpressionWrapper, FloatField
from django.utils import timezone
from django.db.models.functions import TruncDate
import logging
import matplotlib
matplotlib.use('Agg')  # Используем небазовый бэкенд перед импортом pyplot
import matplotlib.pyplot as plt
from aiogram.types import BufferedInputFile
import io
import datetime
import asyncio  # Импортируем asyncio

logger = logging.getLogger('telegramadmin_bot')

router = Router()

async def is_admin(user_id):
    return user_id in ADMIN_TELEGRAM_IDS

@router.message(Command(commands=['analytics']))
async def order_analytics(message: types.Message):
    if not await is_admin(message.from_user.id):
        await message.reply("🚫 **У вас нет доступа к этому боту.**")
        return

    try:
        # Убедимся, что команда вызывается только как /analytics без аргументов
        if not message.text or message.text.strip() != "/analytics":
            await message.reply("❗ **Некорректный формат команды. Используйте только:** `/analytics`")
            return

        # Установим период: последние 30 дней
        end_datetime = timezone.now()
        start_datetime = end_datetime - timezone.timedelta(days=30)

        # Общие метрики
        total_orders = await sync_to_async(Order.objects.filter(created_at__range=(start_datetime, end_datetime)).count)()
        total_sales = (await sync_to_async(Order.objects.filter(created_at__range=(start_datetime, end_datetime)).aggregate)(total_sales=Sum('total_price')))['total_sales'] or 0
        orders_per_status = await sync_to_async(list)(
            Order.objects.filter(created_at__range=(start_datetime, end_datetime))
                        .values('status')
                        .annotate(count=Count('id'))
        )

        # Аналитика по времени
        orders_per_day = await sync_to_async(list)(
            Order.objects.filter(created_at__range=(start_datetime, end_datetime))
                        .annotate(day=TruncDate('created_at'))
                        .values('day')
                        .annotate(count=Count('id'))
                        .order_by('day')
        )

        sales_per_day = await sync_to_async(list)(
            Order.objects.filter(created_at__range=(start_datetime, end_datetime))
                        .annotate(day=TruncDate('created_at'))
                        .values('day')
                        .annotate(total_sales=Sum('total_price'))
                        .order_by('day')
        )

        # Топ-товаров
        best_selling_products = await sync_to_async(list)(
            Order.objects.values('order_items__product__name')
                        .annotate(total_quantity=Sum('order_items__quantity'))
                        .order_by('-total_quantity')[:5]
        )

        highest_revenue_products = await sync_to_async(list)(
            Order.objects.values('order_items__product__name')
                        .annotate(total_revenue=Sum(ExpressionWrapper(F('order_items__quantity') * F('order_items__product__price'), output_field=FloatField())))
                        .order_by('-total_revenue')[:5]
        )

        # Средняя стоимость заказа
        average_order_value = total_sales / total_orders if total_orders else 0

        # Клиентская аналитика
        unique_customers = await sync_to_async(Order.objects.filter(created_at__range=(start_datetime, end_datetime)).values('user').distinct().count)()
        new_customers = await sync_to_async(Order.objects.filter(
            created_at__range=(start_datetime, end_datetime),
            user__orders__created_at__lt=start_datetime  # Используем related_name='orders'
        ).values('user').distinct().count)()
        returning_customers = unique_customers - new_customers

        # Проверяем наличие данных для построения графика
        if not orders_per_day:
            await message.reply("📉 **Нет данных для построения графика.**")
        else:
            buf = io.BytesIO()

            # Предположим, что `orders_per_day` и `sales_per_day` уже содержат соответствующие данные
            days = [item['day'] for item in orders_per_day]
            order_counts = [item['count'] for item in orders_per_day]
            sales = [item['total_sales'] for item in sales_per_day]
            def plot():
                fig, ax1 = plt.subplots(figsize=(10, 5))

                # Линия количества заказов
                ax1.plot(days, order_counts, marker='o', linestyle='-', color='blue', label="Количество заказов")
                ax1.set_xlabel('Дата')
                ax1.set_ylabel('Количество заказов', color='blue')
                ax1.tick_params(axis='y', labelcolor='blue')

                # Вторая ось для продаж
                ax2 = ax1.twinx()
                ax2.plot(days, sales, marker='x', linestyle='--', color='green', label="Продажи")
                ax2.set_ylabel('Продажи (₽)', color='green')
                ax2.tick_params(axis='y', labelcolor='green')

                fig.tight_layout()
                plt.title('Продажи и количество заказов по дням')
                plt.grid(True)
                plt.savefig(buf, format='png')
                plt.close()

            # Запуск построения графика в отдельном потоке
            await asyncio.to_thread(plot)
            buf.seek(0)

            # Обернем буфер в BufferedInputFile для отправки
            input_file = BufferedInputFile(buf.getvalue(), filename='sales_and_orders_per_day.png')

            await message.reply_photo(
                input_file,
                caption="📊 **График количества заказов и продаж по дням** 📊",
                parse_mode='Markdown'
            )

        # Формирование текстового ответа
        response = (
            f"📊 **Аналитика по заказам за последние 30 дней** 📊\n\n"
            f"🔢 **Всего заказов:** {total_orders}\n"
            f"💰 **Общая сумма продаж:** {total_sales} ₽\n"
            f"📈 **Средняя стоимость заказа:** {average_order_value:.2f} ₽\n\n"
            f"👥 **Клиентская аналитика:**\n"
            f"- 🆔 **Уникальные клиенты:** {unique_customers}\n"
            f"- 🆕 **Новые клиенты:** {new_customers}\n"
            f"- 🔄 **Возвращающиеся клиенты:** {returning_customers}\n\n"
            f"📂 **Заказы по статусам:**\n"
        )
        for status_item in orders_per_status:
            status_display = dict(Order.STATUS_CHOICES).get(status_item['status'], status_item['status'])
            response += f"- 🟢 {status_display}: {status_item['count']}\n"

        response += f"\n📅 **Заказы по дням:**\n"
        for day_item in orders_per_day:
            day = day_item['day'].strftime('%Y-%m-%d')
            count = day_item['count']
            response += f"- {day}: {count} \n"

        response += f"\n💵 **Продажи по дням:**\n"
        for sale_item in sales_per_day:
            day = sale_item['day'].strftime('%Y-%m-%d')
            sales = sale_item['total_sales'] or 0
            response += f"- {day}: {sales} ₽ \n"

        response += f"\n🏆 **Топ-5 самых продаваемых товаров:**\n"
        for product in best_selling_products:
            product_name = product['order_items__product__name']
            quantity = product['total_quantity']
            response += f"- {product_name}: {quantity} шт. \n"

        response += f"\n💸 **Топ-5 товаров с наибольшей выручкой:**\n"
        for product in highest_revenue_products:
            product_name = product['order_items__product__name']
            revenue = product['total_revenue'] or 0
            response += f"- {product_name}: {revenue} ₽ \n"

        await message.reply(response, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Ошибка при генерации аналитики: {e}")
        await message.reply("⚠️ **Произошла ошибка при генерации аналитики.**")
