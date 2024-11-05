# orders/apps.py

from django.apps import AppConfig

class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'

    def ready(self):
        # Импортируем сигналы, чтобы они были зарегистрированы
        import orders.signals  # noqa
