# users/tests/test_views.py

from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

class UserAPITest(APITestCase):

    def setUp(self):
        self.admin_user = User.objects.create_superuser(username='admin', password='password')
        self.user = User.objects.create_user(username='testuser', password='password', telegram_id='123456')
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)

    def test_link_telegram_id(self):
        url = reverse('users:link_telegram_id')
        data = {
            'username': 'newuser',
            'telegram_id': '654321'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 404)

    def test_get_token_by_telegram_id(self):
        url = reverse('users:get_token_by_telegram_id') + '?telegram_id=123456'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
