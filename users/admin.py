from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    # Добавляем новые поля в существующие fieldsets
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone', 'address', 'telegram_id')}),
    )

    # Если вы хотите отображать новые поля при добавлении пользователя через админку,
    # необходимо обновить add_fieldsets
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('phone', 'address', 'telegram_id')}),
    )

    # Опционально: отображение новых полей в списке пользователей
    list_display = UserAdmin.list_display + ('phone', 'telegram_id', 'address')


admin.site.register(CustomUser, CustomUserAdmin)
