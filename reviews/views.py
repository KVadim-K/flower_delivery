# reviews/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from products.models import Product
from .models import Review
from .forms import ReviewForm
from orders.models import Order
from django.contrib import messages  # Импортируем сообщения

# Проверка Заказов: Функция has_ordered проверяет, есть ли у пользователя заказ, содержащий данный продукт.
# Отображение Сообщения: Если пользователь не заказывал продукт, отображается соответствующее сообщение.
# Ограничение на Однократный Отзыв: Проверяем, не оставлял ли пользователь уже отзыв на этот продукт.
# Если да, добавляем ошибку в форму.

from django.contrib import messages  # Импортируем сообщения

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Проверяем, сделал ли пользователь заказ на этот продукт
    has_ordered = Order.objects.filter(
        user=request.user,
        order_items__product=product
    ).exists()

    if not has_ordered:
        return render(request, 'reviews/cannot_add_review.html', {'product': product})

    # Проверяем, не оставлял ли пользователь уже отзыв на этот продукт
    existing_review = Review.objects.filter(user=request.user, product=product).first()
    if existing_review:
        # Добавляем сообщение об ошибке
        messages.error(request, "Вы уже оставили отзыв на этот продукт.")
        return redirect('products:product_detail', pk=product.id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            messages.success(request, "Ваш отзыв был успешно добавлен.")
            return redirect('products:product_detail', pk=product.id)
    else:
        form = ReviewForm()

    return render(request, 'reviews/add_review.html', {'form': form, 'product': product})
