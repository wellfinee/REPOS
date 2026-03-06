# studiumx_main/settings/base.py
from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path

import environ


# -----------------------------------------------------------------------------
# Paths & env
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
)

environ.Env.read_env(BASE_DIR / ".env")
if "DJANGO_ALLOWED_HOSTS" in os.environ and "ALLOWED_HOSTS" not in os.environ:
    os.environ["ALLOWED_HOSTS"] = os.environ["DJANGO_ALLOWED_HOSTS"]


print("ENV DB_HOST:", os.getenv("DB_HOST"))
print("ENV DB_PORT:", os.getenv("DB_PORT"))
print("ENV DB_NAME:", os.getenv("DB_NAME"))
print("ENV DB_USER:", os.getenv("DB_USER"))
print("ENV DATABASE_URL:", os.getenv("DATABASE_URL"))
# -----------------------------------------------------------------------------
# Core
# -----------------------------------------------------------------------------
DEBUG = env.bool("DEBUG", default=False)
SECRET_KEY = env("SECRET_KEY")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# -----------------------------------------------------------------------------
# Applications
# -----------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts"
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "axes",
    "django_redis",
"whitenoise.runserver_nostatic",
]


JWT_ACCESS_TTL = timedelta(minutes=5)
JWT_REFRESH_TTL = timedelta(days=7)

JWT_ALGORITHM = "HS256"

JWT_SECRET = SECRET_KEY
LOCAL_APPS = [
    "dbschema",
    "schools",
    "authcore"
]
AUTH_REFRESH_TTL_REMEMBER_SECONDS = 60 * 60 * 24 * 7
AUTH_REFRESH_TTL_SESSION_SECONDS  = 60 * 60 * 24
AUTH_COOKIE_SECURE = False          # ✅ для dev на http
AUTH_COOKIE_SAMESITE = "Lax"        # ✅ для dev
AUTH_COOKIE_DOMAIN = None
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

AUTH_USER_MODEL = "accounts.User"
# -----------------------------------------------------------------------------
# Middleware
# -----------------------------------------------------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
    # axes лучше в конце, после auth
    "axes.middleware.AxesMiddleware",
]

CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:")
CSP_FONT_SRC = ("'self'", "data:")
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"


# -----------------------------------------------------------------------------
# URLs / WSGI
# -----------------------------------------------------------------------------
ROOT_URLCONF = "studiumx_main.urls"
WSGI_APPLICATION = "studiumx_main.wsgi.application"


# -----------------------------------------------------------------------------
# Templates
# -----------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]


# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
        "CONN_MAX_AGE": env.int("DB_CONN_MAX_AGE", default=60),
    }
}


# -----------------------------------------------------------------------------
# Redis / Celery / Cache
# -----------------------------------------------------------------------------
REDIS_URL = env("REDIS_URL", default="redis://127.0.0.1:6379/1")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}


# -----------------------------------------------------------------------------
# DRF
# -----------------------------------------------------------------------------
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "studiumx_main.utils.custom_exception_handler",

    "DEFAULT_AUTHENTICATION_CLASSES": (
        "studiumx_main.authentication.AccessJWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),

    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": "50/min",
        "user": "300/min",
        "login": "10/min",
        "register": "5/min",
        "login_user": "20/min",
    },
}


# -----------------------------------------------------------------------------
# Auth / Axes
# -----------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesBackend",
    "django.contrib.auth.backends.ModelBackend",
    "accounts.auth_backends.EmailOrPhoneBackend",
]

AXES_ENABLED = True
AXES_FAILURE_LIMIT = env.int("AXES_FAILURE_LIMIT", default=5)
AXES_COOLOFF_TIME = env.float("AXES_COOLOFF_TIME", default=1)  # hours
AXES_LOCKOUT_PARAMETERS = ["username", "ip_address"]
AXES_RESET_ON_SUCCESS = True

# хранить в кеше (Redis)
AXES_HANDLER = "axes.handlers.cache.AxesCacheHandler"


# -----------------------------------------------------------------------------
# Custom JWT
# -----------------------------------------------------------------------------

JWT_ISSUER = "studiumx"
# -----------------------------------------------------------------------------
# CORS / CSRF
# -----------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=[
        "http://localhost:5173",
        "https://studiumx.uz",
    ],
)
CORS_ALLOW_CREDENTIALS = True
# если фронт на другом домене и ты используешь cookie-авторизацию —
# тогда понадобится CSRF_TRUSTED_ORIGINS. Для JWT Bearer обычно не нужно,
# но безопасно указать для прод-домена:
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=[
        "https://studiumx.uz",
    ],
)


# -----------------------------------------------------------------------------
# I18N / TZ
# -----------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = env("TIME_ZONE", default="UTC")
USE_I18N = True
USE_TZ = True


# -----------------------------------------------------------------------------
# Static
# -----------------------------------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATIC_ROOT = BASE_DIR / "staticfiles"  # удобно для collectstatic


# -----------------------------------------------------------------------------
# Password validation
# -----------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 12}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# -----------------------------------------------------------------------------
# Security defaults
# -----------------------------------------------------------------------------
X_FRAME_OPTIONS = "DENY"

# reverse proxy (nginx)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": env("LOG_LEVEL", default="INFO"),
    },
}

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
# SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Celery core
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default=CELERY_BROKER_URL)

CELERY_TIMEZONE = env("CELERY_TIMEZONE", default="Asia/Tashkent")
CELERY_ENABLE_UTC = False  # если у тебя всё в локальном TZ и расписания beat по месту

# Serialization (safe defaults)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

# Dev-friendly switch (чтобы можно было разрабатывать без воркера)
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=False)
CELERY_TASK_EAGER_PROPAGATES = env.bool("CELERY_TASK_EAGER_PROPAGATES", default=True)

# Reliability / correctness in prod
CELERY_TASK_ACKS_LATE = True              # ack только после успешного выполнения
CELERY_TASK_REJECT_ON_WORKER_LOST = True  # если воркер умер — задача вернётся в очередь
CELERY_WORKER_PREFETCH_MULTIPLIER = env.int("CELERY_WORKER_PREFETCH_MULTIPLIER", default=1)

# Time limits (то, что ты уже видел)
CELERY_TASK_TIME_LIMIT = env.int("CELERY_TASK_TIME_LIMIT", default=300)        # hard
CELERY_TASK_SOFT_TIME_LIMIT = env.int("CELERY_TASK_SOFT_TIME_LIMIT", default=240)  # soft

# Broker transport options (важно для Redis)
CELERY_BROKER_TRANSPORT_OPTIONS = {
    "visibility_timeout": env.int("CELERY_VISIBILITY_TIMEOUT", default=3600),  # > max duration tasks
    "socket_connect_timeout": env.int("CELERY_SOCKET_CONNECT_TIMEOUT", default=5),
    "socket_timeout": env.int("CELERY_SOCKET_TIMEOUT", default=30),
    "retry_on_timeout": True,
}

# Connection behavior
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Results hygiene (чтобы не засорять backend)

CELERY_RESULT_EXPIRES = env.int("CELERY_RESULT_EXPIRES", default=3600)

