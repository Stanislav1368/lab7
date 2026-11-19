"""
Настройки Django для учебного проекта «Интернет-магазин кофе».

Все значения, зависящие от окружения (БД, секретный ключ, CORS),
читаются из переменных окружения, которые прокидываются через docker compose (.env).
"""
import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def env_list(name: str, default: str = "") -> list[str]:
    """Разбирает строку вида 'a,b,c' из переменной окружения в список."""
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


# --- Базовая безопасность -------------------------------------------------
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-insecure-secret-key-change-me")
DEBUG = os.getenv("DEBUG", "1") == "1"
# В dev сюда попадают localhost/127.0.0.1 и имя сервиса backend.
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1,backend")

# --- Приложения -----------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # сторонние
    "rest_framework",
    "corsheaders",
    # локальные
    "users",
    "shop",
    "reports",
]

MIDDLEWARE = [
    # CorsMiddleware должен идти как можно выше — до CommonMiddleware.
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # DIRS — сюда кладём переопределённые шаблоны админки (templates/admin/base_site.html).
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- База данных ----------------------------------------------------------
# Параметры приходят из .env; POSTGRES_HOST внутри docker-сети = "db".
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "coffee"),
        "USER": os.getenv("POSTGRES_USER", "coffee"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "coffee"),
        "HOST": os.getenv("POSTGRES_HOST", "db"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}

# Кастомная модель пользователя — обязательна до первой миграции.
AUTH_USER_MODEL = "users.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True

# --- Статика и медиа ------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Картинки товаров: в dev Django отдаёт их сам (см. config/urls.py),
# в docker они лежат в volume media_data.
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- DRF + JWT ------------------------------------------------------------
REST_FRAMEWORK = {
    # Единственный способ аутентификации — JWT в заголовке Authorization: Bearer ...
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    # По умолчанию API открыт; ограничения задаются во вьюхах через permission_classes.
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=2),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# --- CORS (dev) -----------------------------------------------------------
# Фронтенд ходит на Vite (5173), Vite проксирует /api на backend,
# но CORS всё равно настраиваем — требование задания и запас на прямой вызов :8000.
CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
)
CORS_ALLOW_CREDENTIALS = True

if DEBUG:
    CSRF_TRUSTED_ORIGINS = env_list(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    )
