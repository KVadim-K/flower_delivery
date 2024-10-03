from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from cart.models import Cart, CartItem
from .models import Order, OrderItem
from django.utils import timezone


@login_required
def create_order(request):
    cart = Cart.objects.get(user=request.user)

    # Отладочное сообщение для проверки товаров в корзине
    print(f"Товары в корзине: {[item.product.name for item in cart.items.all()]}")

    if not cart.items.all():
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        # Создаём заказ
        order = Order.objects.create(
            user=request.user,
            status='pending',
            created_at=timezone.now()
        )

        # Переносим товары из корзины в OrderItem
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity
            )

        # Очищаем корзину после создания заказа
        cart.items.all().delete()

        return redirect('orders:order_history')

    return render(request, 'orders/create_order.html', {'cart': cart})


@login_required
def order_history(request):
    # Сортируем заказы по дате создания в убывающем порядке
    orders = Order.objects.filter(user=request.user).prefetch_related('order_items').order_by('-created_at')

    for order in orders:
        total_price = 0
        for item in order.order_items.all():
            total_price += item.quantity * item.product.price
        order.total_price = total_price  # Добавляем атрибут для отображения в шаблоне

    return render(request, 'orders/order_history.html', {'orders': orders})


@login_required
def reorder(request, order_id):
    original_order = get_object_or_404(Order, id=order_id, user=request.user)

    # Проверяем, есть ли товары в заказе
    if not original_order.order_items.exists():
        print("Исходный заказ не содержит товаров.")
        return redirect('orders:order_history')

    # Получаем или создаём корзину пользователя
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Переносим товары из заказа в корзину
    for item in original_order.order_items.all():
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=item.product)
        if created:
            cart_item.quantity = item.quantity  # Если товар новый, добавляем количество
        else:
            cart_item.quantity += item.quantity  # Если товар уже есть, увеличиваем количество
        cart_item.save()

    # Перенаправляем пользователя на страницу корзины
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





