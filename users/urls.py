# users/urls.py

from django.urls import path
from . import views
from .views import GetTokenByTelegramIDAPIView

urlpatterns = [
    path('api/link_telegram_id/', views.link_telegram_id, name='link_telegram_id'),
    path('api/get_token_by_telegram_id/', views.get_token_by_telegram_id, name='get_token_by_telegram_id'),
]
