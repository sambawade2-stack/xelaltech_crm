from .base import *

DEBUG = False

# ── Sécurité derrière Traefik (Dokploy) ──────────────────────────────────────
# Traefik termine le SSL et forward le trafic en HTTP.
# On ne redirige PAS vers HTTPS dans l'app (Traefik le fait).
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

# Obligatoire Django 4+ derrière un proxy HTTPS
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])

CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])

# ── Cache : base de données (pas besoin de Redis) ─────────────────────────────
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache',
    }
}

# ── Celery : broker Redis optionnel ───────────────────────────────────────────
CELERY_BROKER_URL = env('REDIS_URL', default='redis://redis:6379/0')
CELERY_RESULT_BACKEND = 'django-db'

# ── Allauth rate limiting (utilise le cache DB) ───────────────────────────────
ACCOUNT_RATE_LIMITS = {
    'login_failed': '5/5m',
    'signup':       '5/h',
    'password_reset': '3/h',
}

# ── Logging vers stdout (Docker / Dokploy) ────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {'format': '{levelname} {asctime} {module} {message}', 'style': '{'},
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'simple'},
    },
    'root': {'handlers': ['console'], 'level': 'INFO'},
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'WARNING', 'propagate': False},
        'apps': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
    },
}
