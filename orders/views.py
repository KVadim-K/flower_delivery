from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from cart.models import Cart, CartItem
from .models import Order
from django.utils import timezone

@login_required
def create_order(request):
    cart = Cart.objects.get(user=request.user)
    if not cart.items.all():
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user,
            status='pending',
            created_at=timezone.now()
        )
        order.items.set(cart.items.all())
        order.save()
        cart.items.all().delete()
        return redirect('orders:order_history')

    return render(request, 'orders/create_order.html', {'cart': cart})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})
