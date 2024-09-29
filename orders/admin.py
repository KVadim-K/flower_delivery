from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'order_date']
    list_filter = ['status', 'order_date']
    inlines = [OrderItemInline]

admin.site.register(Order, OrderAdmin)
