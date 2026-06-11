"""Ratings app configuration."""

from __future__ import annotations

from django.apps import AppConfig


class RatingsConfig(AppConfig):
    """Configuration for rating domain models."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.ratings"
