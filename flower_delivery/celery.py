# flowre_delivery/celery.py

import os
import django
from celery import Celery

# Устанавливаем модуль настроек для Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flower_delivery.settings')

# Настройка Django перед инициализацией Celery
django.setup()

# Создаем приложение Celery
app = Celery('flower_delivery')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
