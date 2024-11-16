# settings.py

from pathlib import Path
import os
from dotenv import load_dotenv

# Определение BASE_DIR для поиска .env
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / 'telegram_bot' / '.env'

# Загрузка переменных окружения
load_dotenv(dotenv_path=env_path)

# Переменные для основного бота
BOT_TOKEN = os.getenv('BOT_TOKEN')
API_URL = os.getenv('API_URL')
SITE_URL = os.getenv('SITE_URL')
TELEGRAM_IDS_RAW = os.getenv('TELEGRAM_IDS', '')
TELEGRAM_IDS = [int(id.strip()) for id in TELEGRAM_IDS_RAW.split(',') if id.strip().isdigit()]

# Переменные для административного бота
ADMIN_BOT_TOKEN = os.getenv('ADMIN_BOT_TOKEN')
ADMIN_TELEGRAM_IDS_RAW = os.getenv('ADMIN_TELEGRAM_IDS', '')
ADMIN_TELEGRAM_IDS = [int(id.strip()) for id in ADMIN_TELEGRAM_IDS_RAW.split(',') if id.strip().isdigit()]
ADMIN_API_TOKEN = os.getenv('ADMIN_API_TOKEN')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-%+wty+6+g8negp0b4lml(%$zw*z6=4#@zvjr=%oe#3g^iyrks1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*", "web", "localhost", "127.0.0.1", "213.171.31.251", "example.com"]


# Application definition

INSTALLED_APPS = [
    # Стандартные приложения Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'django_celery_results',

    # Необходимо для django-allauth
    'django.contrib.sites',

    # Сторонние приложения
    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    # Другие сторонние приложения (например, для аналитики)
    'rest_framework',
    'rest_framework.authtoken',

    # Ваши приложения
    'users.apps.UsersConfig',
    'products.apps.ProductsConfig',
    'cart.apps.CartConfig',
    'orders.apps.OrdersConfig',
    'reviews.apps.ReviewsConfig',
    'reports.apps.ReportsConfig',
    'telegram_bot',  # Добавляем telegram_bot
    'telegramadmin_bot',   # Новый админ-бот
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Добавлено здесь
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'flower_delivery.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Создайте папку templates в корне проекта
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # Необходимо для django-allauth
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'flower_delivery.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'  # Для московского времени

USE_I18N = True

USE_TZ = True

AUTH_USER_MODEL = 'users.CustomUser'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'


MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Стандартный бэкенд Django
    'allauth.account.auth_backends.AuthenticationBackend',  # Бэкенд для django-allauth
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}


SITE_ID = 1

# Django Allauth Settings
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none'  # 'none', 'mandatory', 'optional'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

DEFAULT_FROM_EMAIL = 'd3liveryflower@yandex.ru'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False  # Не включайте одновременно SSL и TLS
EMAIL_HOST_USER = 'd3liveryflower@yandex.ru'
EMAIL_HOST_PASSWORD = 'mowljpghjgotaegj'

# Настройки для Celery
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Moscow'
# Настройка для хранения результатов задач Celery в базе данных Django
CELERY_RESULT_BACKEND = 'django-db'



LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'admin_bot_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'admin_bot.log',
            'encoding': 'utf-8',  # Добавлено для корректного отображения UTF-8
        },
        'telegram_bot_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'telegram_bot.log',
            'encoding': 'utf-8',  # Добавлено для корректного отображения UTF-8
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'error.log',
            'encoding': 'utf-8',  # Добавлено для корректного отображения UTF-8
        },
    },
    'loggers': {
        'telegramadmin_bot': {
            'handlers': ['console', 'admin_bot_file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'telegram_bot': {
            'handlers': ['console', 'telegram_bot_file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django': {
            'handlers': ['console', 'error_file'],
            'level': 'ERROR',
            'propagate': True,
        },
        '': {
            'handlers': ['console', 'error_file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}


# # Загрузка переменных окружения
# print(f"API_URL from settings: {API_URL}")
# print(f"ADMIN_TELEGRAM_IDS from settings: {ADMIN_TELEGRAM_IDS}")
