"""Accounts app configuration."""

from __future__ import annotations

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Configuration for identity and authentication."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
