# orders/admin.py

from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at', 'total_price', 'address', 'city', 'postal_code', 'phone_number')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]
    search_fields = ('user__username', 'id')
    readonly_fields = ('created_at', 'total_price')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity')
    list_filter = ('product',)
    search_fields = ('order__id', 'product__name')
