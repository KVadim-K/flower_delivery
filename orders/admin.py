from django.contrib import admin
from .models import Order

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username',)

admin.site.register(Order, OrderAdmin)
