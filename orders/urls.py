from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/<int:product_id>/', views.create_order, name='create_order'),
    path('create/', views.create_order, name='create_order_no_id'),  # маршрут без product_id
    path('history/', views.order_history, name='order_history'),
    path('reorder/<int:order_id>/', views.reorder, name='reorder'),
    path('update/', views.update_cart, name='update_cart'),
    path('api/create/', views.CreateOrderAPIView.as_view(), name='api_create_order'),
    path('api/status/<int:order_id>/', views.OrderStatusAPIView.as_view(), name='api_order_status'),
    path('api/analytics/', views.OrderAnalyticsAPIView.as_view(), name='api_order_analytics'),

    # API эндпоинты
    path('api/create/', views.CreateOrderAPIView.as_view(), name='api_create_order'),
]

