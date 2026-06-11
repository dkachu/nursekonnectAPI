"""Celery application configuration for NurseKonnect."""

from __future__ import annotations

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.production")

app = Celery("nursekonnect")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
