# users/views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
import json

@csrf_exempt
def link_telegram_id(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        telegram_id = data.get('telegram_id')

        try:
            user = get_user_model().objects.get(username=username)
            user.telegram_id = telegram_id
            user.save()
            return JsonResponse({'message': 'Success'})
        except get_user_model().DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def get_token_by_telegram_id(request):
    if request.method == 'GET':
        telegram_id = request.GET.get('telegram_id')

        try:
            user = get_user_model().objects.get(telegram_id=telegram_id)
            token, created = Token.objects.get_or_create(user=user)
            return JsonResponse({'token': token.key})
        except get_user_model().DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

    return JsonResponse({'error': 'Invalid request method'}, status=400)