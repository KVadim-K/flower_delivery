# orders/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Order, OrderItem
from telegramadmin_bot.tasks import send_notification_to_admins

@receiver(post_save, sender=OrderItem)
@receiver(post_delete, sender=OrderItem)
def update_order_total_price(sender, instance, **kwargs):
    # Пересчитываем `total_price` каждый раз при изменении `OrderItem`
    order = instance.order
    order.update_total_price()

    # Уведомление администраторам при добавлении или изменении заказа
    if kwargs.get('created', False):
        send_notification_to_admins.delay(order.id)
