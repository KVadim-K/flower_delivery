from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    # Добавление полей в форму редактирования существующих пользователей
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('phone', 'address', 'telegram_id')}),
    )

    # Добавление полей в форму создания новых пользователей
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {'fields': ('phone', 'address', 'telegram_id')}),
    )

    # Опционально: отображение новых полей в списке пользователей
    list_display = UserAdmin.list_display + ('phone', 'telegram_id', 'address')

# Регистрация модели CustomUser с новым админ-классом
admin.site.register(CustomUser, CustomUserAdmin)
