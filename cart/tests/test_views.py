# cart/tests/test_views.py

from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from products.models import Product
from cart.models import Cart, CartItem

User = get_user_model()

class CartViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.product = Product.objects.create(name='Test Product', price=100.00)
        self.client.login(username='testuser', password='password')

    def test_add_to_cart(self):
        url = reverse('cart:add_to_cart', args=[self.product.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to cart detail
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.items.first().product.name, 'Test Product')
