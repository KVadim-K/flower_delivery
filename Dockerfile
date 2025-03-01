# Используем базовый образ Python 3.12
FROM python:3.12

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл требований
COPY requirements.txt /app/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . /app/

# Открываем порт 8000
EXPOSE 8000

# Команда для запуска сервера Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
