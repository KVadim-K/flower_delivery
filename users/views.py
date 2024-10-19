# users/views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json

User = get_user_model()

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


class GetTokenByTelegramIDAPIView(APIView):
    def get(self, request):
        telegram_id = request.query_params.get('telegram_id')
        if not telegram_id:
            return Response({"error": "Необходимо указать telegram_id."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(profile__telegram_id=telegram_id)
            token = user.auth_token.key  # Предполагается, что вы используете TokenAuthentication
            return Response({"token": token}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": f"Пользователь с telegram_id {telegram_id} не найден."},
                            status=status.HTTP_404_NOT_FOUND)