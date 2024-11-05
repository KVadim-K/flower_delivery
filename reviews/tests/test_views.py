# reviews/tests/test_views.py

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from products.models import Product
from reviews.models import Review
from orders.models import Order, OrderItem

User = get_user_model()

class ReviewViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.product = Product.objects.create(name='Test Product', price=100.00)
        self.order = Order.objects.create(user=self.user)
        OrderItem.objects.create(order=self.order, product=self.product, quantity=1)
        self.client.login(username='testuser', password='password')

    def test_add_review(self):
        url = reverse('reviews:add_review', args=[self.product.id])
        data = {
            'rating': 5,
            'comment': 'Great product!'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.first().comment, 'Great product!')
