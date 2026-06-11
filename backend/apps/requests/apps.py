"""Care requests app configuration."""

from __future__ import annotations

from django.apps import AppConfig


class RequestsConfig(AppConfig):
    """Configuration for care request domain models."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.requests"
