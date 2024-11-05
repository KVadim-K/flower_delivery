#  orders/tests/test_views.py

from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from products.models import Product
from orders.models import Order, OrderItem

User = get_user_model()

class OrderAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.product = Product.objects.create(name='Test Product', price=100.00)

    def test_create_order(self):
        url = reverse('orders:api_create_order')
        data = {
            "order_items": [
                {"product": self.product.id, "quantity": 2}
            ],
            "address": "123 Main St",
            "city": "Test City",
            "postal_code": "123456",
            "phone_number": "+71234567890"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)
        self.assertEqual(OrderItem.objects.first().quantity, 2)

    def test_get_user_orders(self):
        Order.objects.create(user=self.user, total_price=200.00)
        url = reverse('orders:api_user_orders')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
