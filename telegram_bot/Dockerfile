# Используем базовый образ Python 3.12
FROM python:3.12

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл требований из корневой директории проекта
COPY requirements.txt /app/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код бота
COPY telegram_bot/ /app/

# Команда для запуска бота
CMD ["python", "telegram_bot/bot/main.py"]
