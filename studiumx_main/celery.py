import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", os.getenv("DJANGO_SETTINGS_MODULE", "studiumx_main.settings"))

app = Celery("studiumx")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()