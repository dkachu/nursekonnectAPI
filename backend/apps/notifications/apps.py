"""Notifications app configuration."""

from __future__ import annotations

from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    """Configuration for notification domain models."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.notifications"
