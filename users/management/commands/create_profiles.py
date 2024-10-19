# users/management/commands/create_profiles.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Profile

class Command(BaseCommand):
    help = 'Создает профили для пользователей, у которых они отсутствуют'

    def handle(self, *args, **options):
        User = get_user_model()
        users_without_profile = User.objects.filter(profile__isnull=True)
        count = users_without_profile.count()
        for user in users_without_profile:
            Profile.objects.create(user=user)
            self.stdout.write(self.style.SUCCESS(f'Создан профиль для пользователя: {user.username}'))
        self.stdout.write(self.style.SUCCESS(f'Всего создано профилей: {count}'))
