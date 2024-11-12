# users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    telegram_id = models.CharField(max_length=50, blank=True, null=True, unique=True)

    def __str__(self):
        return self.username

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    # Добавьте дополнительные поля профиля, если необходимо

    def __str__(self):
        return f"Профиль пользователя {self.user.username}"

@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender: 'CustomUser', instance: CustomUser, created: bool, **kwargs):
    # Создаем профиль или получаем существующий
    Profile.objects.get_or_create(user=instance)
    # Если профиль уже существует, его можно обновить при необходимости
    if not created:
        instance.profile.save()

