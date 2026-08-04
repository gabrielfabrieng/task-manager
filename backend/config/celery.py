"""Celery application factory."""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("todo")
# Read config from Django settings, CELERY_ namespaced keys.
app.config_from_object("django.conf:settings", namespace="CELERY")
# Auto-discover tasks.py in every installed app.
app.autodiscover_tasks()
