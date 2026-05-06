"""
Production settings — branch: main
Always use .env.prod with real secrets.
"""
from .base import *

DEBUG = False
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# HTTPS security (enable when behind HTTPS termination)
SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT', default=False)
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {'format': '{levelname} {asctime} {module} {message}', 'style': '{'},
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/django.log',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {'class': 'logging.StreamHandler', 'formatter': 'verbose'},
    },
    'root': {'handlers': ['file', 'console'], 'level': 'WARNING'},
    'loggers': {
        'django': {'handlers': ['file'], 'level': 'WARNING', 'propagate': False},
        'django.security': {'handlers': ['file'], 'level': 'ERROR', 'propagate': False},
    },
}
