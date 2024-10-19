# products/urls.py

from django.urls import path
from .views import ProductListAPIView, ProductSearchAPIView, product_list, product_detail

app_name = 'products'

urlpatterns = [
    path('', product_list, name='product_list'),
    path('<int:pk>/', product_detail, name='product_detail'),
    path('api/list/', ProductListAPIView.as_view(), name='api_product_list'),
    path('api/search/', ProductSearchAPIView.as_view(), name='api_product_search'),
]
