from django.test import TestCase
from django.contrib.auth import get_user_model
from products.models import Product
from orders.models import Order, OrderItem
from orders.serializers import OrderSerializer
from rest_framework.test import APIRequestFactory

User = get_user_model()


class OrderSerializerTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.product = Product.objects.create(name='Test Product', price=100.00)
        self.order_data = {
            "order_items": [
                {"product": self.product.id, "quantity": 2}
            ],
            "address": "123 Main St",
            "city": "Test City",
            "postal_code": "123456",
            "phone_number": "+71234567890"
        }

    def test_order_serializer(self):
        # Создаем фиктивный запрос и задаем пользователя
        factory = APIRequestFactory()
        request = factory.post('/')  # Тип запроса здесь не важен, можно использовать `post`
        request.user = self.user

        # Добавляем `request` в контекст сериалайзера
        serializer = OrderSerializer(data=self.order_data, context={'request': request})
        self.assertTrue(serializer.is_valid())

        # Сохраняем данные через сериалайзер и проверяем, что они корректны
        order = serializer.save()
        self.assertEqual(order.order_items.first().product.name, 'Test Product')
        self.assertEqual(order.order_items.first().quantity, 2)
