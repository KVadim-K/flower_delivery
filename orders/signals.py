# orders/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from telegramadmin_bot.tasks import send_new_order_notification

@receiver(post_save, sender=Order)
def notify_admins_on_new_order(sender, instance, created, **kwargs):
    if created:
        send_new_order_notification.delay(order_id=instance.id)
