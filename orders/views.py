# orders/views.py

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from cart.models import Cart, CartItem
from .models import Order, OrderItem
from products.models import Product
from django.utils import timezone
from rest_framework import generics, permissions
from .serializers import OrderSerializer, OrderStatusSerializer, OrderAnalyticsSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Order  # Убедитесь, что модель Order существует

# Ваши существующие представления

@login_required
def create_order(request, product_id=None):
    """
    Создание заказа через веб-интерфейс.
    """
    # Получаем корзину текущего пользователя или создаём новую
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Если передан product_id, добавляем товар в корзину
    if product_id:
        product = get_object_or_404(Product, id=product_id)
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
        if item_created:
            cart_item.quantity = 1  # Устанавливаем количество, если товар новый в корзине
        else:
            cart_item.quantity += 1  # Увеличиваем количество, если товар уже добавлен
        cart_item.save()

    # Проверяем, не пуста ли корзина
    if not cart.items.exists():
        return redirect('cart:cart_detail')

    # Обработка создания заказа при POST-запросе
    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user,
            status='pending',
            created_at=timezone.now()
        )

        # Переносим товары из корзины в заказ
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity
            )

        # Вычисляем общую сумму заказа
        total_price = sum(item.product.price * item.quantity for item in order.order_items.all())
        order.total_price = total_price
        order.save()

        # Очищаем корзину после создания заказа
        cart.items.all().delete()

        return redirect('orders:order_history')

    # Рендерим шаблон создания заказа с текущей корзиной
    return render(request, 'orders/create_order.html', {'cart': cart})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('order_items').order_by('-created_at')

    # Вычисляем итоговую сумму для каждого заказа
    for order in orders:
        total_price = 0
        for item in order.order_items.all():
            total_price += item.quantity * item.product.price
        order.total_price = total_price

    return render(request, 'orders/order_history.html', {'orders': orders})


@login_required
def reorder(request, order_id):
    original_order = get_object_or_404(Order, id=order_id, user=request.user)

    if not original_order.order_items.exists():
        print("Исходный заказ не содержит товаров.")
        return redirect('orders:order_history')

    # Получаем или создаём корзину пользователя
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Переносим товары из заказа в корзину
    for item in original_order.order_items.all():
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=item.product)
        if created:
            cart_item.quantity = item.quantity
        else:
            cart_item.quantity += item.quantity
        cart_item.save()

    return redirect('cart:cart_detail')


@login_required
def update_cart(request):
    cart = Cart.objects.get(user=request.user)
    for item in cart.items.all():
        quantity = request.POST.get(f'quantity_{item.id}')
        if quantity:
            try:
                quantity = int(quantity)
                if quantity > 0:
                    item.quantity = quantity
                    item.save()
                else:
                    item.delete()
            except ValueError:
                pass  # Игнорируем некорректные значения
    return redirect('cart:cart_detail')


# Добавление API-представления для создания заказа

class CreateOrderAPIView(generics.CreateAPIView):
    """
    API-представление для создания нового заказа.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# API-представление для проверки статуса заказа
class OrderStatusAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        serializer = OrderStatusSerializer(order)
        return Response(serializer.data)

# API-представление для аналитики заказов
class OrderAnalyticsAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        total_orders = Order.objects.count()
        total_sales = Order.objects.aggregate(Sum('order_items__product__price'))['order_items__product__price__sum'] or 0
        total_profit = total_sales * 0.2
        total_expenses = total_sales * 0.8
        data = {
            'total_orders': total_orders,
            'total_sales': total_sales,
            'total_profit': total_profit,
            'total_expenses': total_expenses,
        }
        serializer = OrderAnalyticsSerializer(data)
        return Response(serializer.data)

class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_items = request.data.get('order_items', [])
        if not order_items:
            return Response({"error": "Необходимо указать order_items."}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(user=request.user)
        for item in order_items:
            product_id = item.get('product')
            quantity = item.get('quantity', 1)
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({"error": f"Продукт с id {product_id} не найден."}, status=status.HTTP_404_NOT_FOUND)

            OrderItem.objects.create(order=order, product=product, quantity=quantity)

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserOrdersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)