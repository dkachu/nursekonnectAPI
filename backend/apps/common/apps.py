"""Common app configuration."""

from __future__ import annotations

from django.apps import AppConfig


class CommonConfig(AppConfig):
    """Configuration for shared foundation models."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.common"
