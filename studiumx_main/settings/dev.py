from .base import *

DEBUG = True

# В dev не включаем принудительный HTTPS и HSTS
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# CORS для локальной разработки можно расширить
CORS_ALLOWED_ORIGINS = list(set(CORS_ALLOWED_ORIGINS + [
    "http://localhost:5173",
]))
