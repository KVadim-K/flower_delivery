# users/urls.py

from django.urls import path
from .views import (
    GetTokenByTelegramIDAPIView,
    LinkTelegramIDAPIView,
)

app_name = 'users'

urlpatterns = [
    path('api/link_telegram_id/', LinkTelegramIDAPIView.as_view(), name='link_telegram_id'),
    path('api/get_token_by_telegram_id/', GetTokenByTelegramIDAPIView.as_view(), name='get_token_by_telegram_id'),
]
