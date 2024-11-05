# orders/tests/test_models.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from products.models import Product
from orders.models import Order, OrderItem

User = get_user_model()

class OrderModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.product = Product.objects.create(name='Test Product', price=100.00)
        self.order = Order.objects.create(user=self.user)
        self.order_item = OrderItem.objects.create(order=self.order, product=self.product, quantity=2)

    def test_order_creation(self):
        self.assertEqual(self.order.user.username, 'testuser')
        self.assertEqual(self.order.total_price, 0.00)  # Assuming default total_price is 0.00

    def test_order_item_creation(self):
        self.assertEqual(self.order_item.product.name, 'Test Product')
        self.assertEqual(self.order_item.quantity, 2)

    def test_order_str(self):
        self.assertEqual(str(self.order), f"Order {self.order.id} by {self.user.username}")

    def test_order_item_str(self):
        self.assertEqual(str(self.order_item), f'2 x Test Product')
