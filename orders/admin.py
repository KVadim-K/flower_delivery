# orders/admin.py

from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """
    Встроенная админка для отображения товаров в заказе.
    """
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity')
    can_delete = False  # Запрет на удаление OrderItem через админку Order
    show_change_link = True  # Позволяет переходить к редактированию OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Настройка админпанели для модели Order.
    """
    # Поля, отображаемые в списке заказов
    list_display = ('id', 'user', 'status_display', 'created_at', 'total_price')

    # Фильтры по статусу, дате создания и пользователю
    list_filter = ('status', 'created_at', 'user')

    # Поля для поиска
    search_fields = ('user__username', 'id')

    # Встроенная админка для OrderItem
    inlines = [OrderItemInline]

    # Порядок сортировки заказов (новые сверху)
    ordering = ('-created_at',)

    # Поля, доступные только для чтения
    readonly_fields = ('created_at', 'total_price')

    # Параметры отображения полей в форме редактирования заказа
    fieldsets = (
        (None, {
            'fields': ('user', 'status', 'address', 'city', 'postal_code', 'phone_number')
        }),
        ('Дополнительно', {
            'fields': ('created_at', 'total_price'),
        }),
    )

    @admin.display(description='Статус')
    def status_display(self, obj):
        """
        Метод для отображения человекочитаемого статуса заказа.
        """
        return obj.get_status_display()


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Настройка админпанели для модели OrderItem.
    """
    list_display = ('id', 'order', 'product', 'quantity')
    list_filter = ('order', 'product')
    search_fields = ('order__id', 'product__name')
    readonly_fields = ('order', 'product', 'quantity')
