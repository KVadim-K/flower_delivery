# orders/models.py

from django.db import models
from django.conf import settings
from products.models import Product
from cart.models import CartItem


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('processing', 'В обработке'),
        ('completed', 'Завершён'),
        ('cancelled', 'Отменён'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(CartItem)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    # Новые поля для данных доставки
    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    # Добавленное поле для общей суммы заказа
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


# Новая модель OrderItem
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'
