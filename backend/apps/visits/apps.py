"""Visits app configuration."""

from __future__ import annotations

from django.apps import AppConfig


class VisitsConfig(AppConfig):
    """Configuration for visit domain models."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.visits"
