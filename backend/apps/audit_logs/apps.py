"""Audit logs app configuration."""

from __future__ import annotations

from django.apps import AppConfig


class AuditLogsConfig(AppConfig):
    """Configuration for audit log domain models."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.audit_logs"
