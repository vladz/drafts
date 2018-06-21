BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = BROKER_URL
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
