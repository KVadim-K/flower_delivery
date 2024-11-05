from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from products.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()

class ProductAPITest(APITestCase):

    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(username='testuser', password='password')
        # Создаем токен для пользователя и добавляем его в клиент
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Создаем тестовые продукты
        self.product1 = Product.objects.create(name='Rose', price=50.00)
        self.product2 = Product.objects.create(name='Tulip', price=30.00)

    def test_product_list(self):
        url = reverse('products:api_product_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)

    def test_product_search(self):
        url = reverse('products:api_product_search') + '?search=Rose'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Rose')
