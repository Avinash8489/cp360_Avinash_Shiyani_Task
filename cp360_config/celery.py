import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cp360_config.settings")

app = Celery("cp360_config")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

