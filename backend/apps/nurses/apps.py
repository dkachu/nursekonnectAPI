"""Nurses app configuration."""

from __future__ import annotations

from django.apps import AppConfig


class NursesConfig(AppConfig):
    """Configuration for nurse domain models."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.nurses"
