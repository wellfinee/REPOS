from .base import *
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration



DEBUG = False

# Security (продакшен)
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True

SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Если у тебя реально S3/MinIO и установлен django-storages + boto3,
# тогда раскомментируй:
# DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# Пример: можно ограничить CORS в проде только доменом:
CORS_ALLOWED_ORIGINS = [
    "https://studiumx.uz",
]


SENTRY_DSN = env("SENTRY_DSN", default="")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        environment=env("SENTRY_ENVIRONMENT", default="production"),
        traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE", default=0.05),
        send_default_pii=False,
    )