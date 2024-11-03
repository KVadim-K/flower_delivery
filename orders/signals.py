# orders/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from telegramadmin_bot.tasks import send_notification_to_admins

@receiver(post_save, sender=Order)
def order_created(sender, instance, created, **kwargs):
    if created:
        # Дополнительная обработка при создании заказа
        # Отправляем уведомление администраторам
        send_notification_to_admins.delay(instance.id)
