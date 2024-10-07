from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from cart.models import Cart, CartItem
from .models import Order, OrderItem
from products.models import Product  # добавлено для работы с моделью Product
from django.utils import timezone


@login_required
def create_order(request, product_id=None):
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
            item.quantity = int(quantity)
            item.save()

    return redirect('cart:cart_detail')
