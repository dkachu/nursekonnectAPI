"""Patients app configuration."""

from __future__ import annotations

from django.apps import AppConfig


class PatientsConfig(AppConfig):
    """Configuration for patient domain models."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.patients"
