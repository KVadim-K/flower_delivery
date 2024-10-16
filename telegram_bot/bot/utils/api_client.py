import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

class APIClient:
    def __init__(self, token: str):
        self.token = token
        self.session = aiohttp.ClientSession()

    async def create_order(self, order_items):
        url = f"{API_URL}/orders/api/create/"
        headers = {
            'Authorization': f'Token {self.token}',
            'Content-Type': 'application/json'
        }
        payload = {
            'order_items': order_items
        }
        async with self.session.post(url, json=payload, headers=headers) as response:
            if response.status == 201:
                return await response.json()
            else:
                error = await response.text()
                raise Exception(f"Не удалось создать заказ: {error}")

    async def get_order_status(self, order_id):
        url = f"{API_URL}/orders/api/status/{order_id}/"
        headers = {
            'Authorization': f'Token {self.token}',
            'Content-Type': 'application/json'
        }
        async with self.session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                error = await response.text()
                raise Exception(f"Не удалось получить статус заказа: {error}")

    async def link_telegram_id(self, username: str, telegram_id: int):
        """
        Связывает Telegram ID с пользователем Django по username.
        """
        url = f"{API_URL}/users/api/link_telegram_id/"
        headers = {
            'Authorization': f'Token {self.token}',
            'Content-Type': 'application/json'
        }
        payload = {
            'username': username,
            'telegram_id': telegram_id
        }
        async with self.session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                error = await response.text()
                raise Exception(f"Не удалось связать Telegram ID: {error}")

    async def get_user_orders(self):
        """
        Получает список заказов пользователя.
        Предполагается наличие эндпоинта /orders/api/user_orders/
        """
        url = f"{API_URL}/orders/api/user_orders/"
        headers = {
            'Authorization': f'Token {self.token}',
            'Content-Type': 'application/json'
        }
        async with self.session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                error = await response.text()
                raise Exception(f"Не удалось получить заказы: {error}")

    async def close(self):
        await self.session.close()

async def get_user_api_token(telegram_id: int) -> str:
    """
    Функция для получения API-токена пользователя по его Telegram ID.
    Предполагается наличие эндпоинта /users/api/get_token_by_telegram_id/?telegram_id=<id>
    """
    token_url = f"{API_URL}/users/api/get_token_by_telegram_id/?telegram_id={telegram_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(token_url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('token')
            return None
