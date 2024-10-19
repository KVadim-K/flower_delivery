# orders/urls.py

from django.urls import path
from .views import (
    CreateOrderAPIView,
    UserOrdersAPIView,
    OrderStatusAPIView,
    OrderAnalyticsAPIView,
    create_order,  # Функция для создания заказа (если используется)
    order_history,
    reorder,
    update_cart,
)

app_name = 'orders'

urlpatterns = [
    # Функциональные представления для веб-интерфейса
    path('create/<int:product_id>/', create_order, name='create_order'),
    path('create/', create_order, name='create_order_no_id'),
    path('history/', order_history, name='order_history'),
    path('reorder/<int:order_id>/', reorder, name='reorder'),
    path('update/', update_cart, name='update_cart'),

    # API эндпоинты - классовые представления
    path('api/create/', CreateOrderAPIView.as_view(), name='api_create_order'),
    path('api/user_orders/', UserOrdersAPIView.as_view(), name='api_user_orders'),
    path('api/status/<int:order_id>/', OrderStatusAPIView.as_view(), name='api_order_status'),
    path('api/analytics/', OrderAnalyticsAPIView.as_view(), name='api_order_analytics'),
]
