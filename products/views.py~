# products/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render, get_object_or_404
from .models import Product
from reviews.models import Review
from django.db.models import Avg
from .serializers import ProductSerializer

def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})

def product_detail(request, pk):
    # Получаем продукт по его id
    product = get_object_or_404(Product, pk=pk)

    # Получаем все отзывы, связанные с текущим продуктом.
    reviews = Review.objects.filter(product=product)

    # Вычисляем средний рейтинг по всем отзывам данного продукта. Если отзывов нет, значение будет None.
    average_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0

    # Рассчитываем заполненные и пустые звёзды на основе среднего рейтинга
    filled_stars = int(average_rating)
    empty_stars = 5 - filled_stars

    return render(request, 'products/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'average_rating': average_rating,
        'filled_stars': filled_stars,
        'empty_stars': empty_stars,
    })
class ProductSearchAPIView(APIView):
    def get(self, request):
        search_query = request.GET.get('search', '')
        products = Product.objects.filter(name__icontains=search_query)
        serializer = ProductSerializer(products, many=True)
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)