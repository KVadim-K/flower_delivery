from django.db import models
from django.conf import settings
from products.models import Product

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    review = models.TextField()
    rating = models.PositiveIntegerField(default=5)

    def __str__(self):
        return f"Review by {self.user.username} on {self.product.name}"
