# orders/serializers.py

from rest_framework import serializers
from .models import Order, OrderItem
from products.models import Product
from django.utils import timezone

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(
        source='product.price',
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['product', 'product_name', 'product_price', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, write_only=True)
    order_items_details = OrderItemSerializer(source='order_items', many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    address = serializers.CharField(max_length=255, required=True)
    city = serializers.CharField(max_length=100, required=True)
    postal_code = serializers.CharField(max_length=20, required=True)
    phone_number = serializers.CharField(max_length=20, required=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'order_items',
            'order_items_details',
            'status',
            'status_display',
            'created_at',
            'address',
            'city',
            'postal_code',
            'phone_number',
            'total_price'
        ]
        read_only_fields = ['user', 'status', 'created_at', 'total_price']

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')
        user = self.context['request'].user
        order = Order.objects.create(
            user=user,
            status='pending',
            created_at=timezone.now(),
            address=validated_data['address'],
            city=validated_data['city'],
            postal_code=validated_data['postal_code'],
            phone_number=validated_data['phone_number']
        )

        total_price = 0
        for item_data in order_items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            OrderItem.objects.create(order=order, product=product, quantity=quantity)
            total_price += product.price * quantity

        order.total_price = total_price
        order.save()
        return order

class OrderStatusSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'status_display', 'created_at']

class OrderAnalyticsSerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    total_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_profit = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
