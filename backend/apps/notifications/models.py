"""Notification domain models."""

from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class NotificationType(models.TextChoices):
    """Supported notification event types."""

    JOB_ASSIGNED = "JOB_ASSIGNED", "Job assigned"
    JOB_ACCEPTED = "JOB_ACCEPTED", "Job accepted"
    JOB_WARNING = "JOB_WARNING", "Job warning"
    JOB_CANCELLED = "JOB_CANCELLED", "Job cancelled"
    NURSE_EN_ROUTE = "NURSE_EN_ROUTE", "Nurse en route"
    NURSE_ARRIVED = "NURSE_ARRIVED", "Nurse arrived"
    VISIT_STARTED = "VISIT_STARTED", "Visit started"
    VISIT_COMPLETED = "VISIT_COMPLETED", "Visit completed"


class NotificationChannel(models.TextChoices):
    """Supported notification delivery channels."""

    PUSH = "PUSH", "Push"
    EMAIL = "EMAIL", "Email"
    SMS = "SMS", "SMS"


class NotificationStatus(models.TextChoices):
    """Notification delivery statuses."""

    PENDING = "PENDING", "Pending"
    SENT = "SENT", "Sent"
    FAILED = "FAILED", "Failed"


class Notification(TimeStampedModel):
    """Persisted notification event for asynchronous delivery."""

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    notification_type = models.CharField(max_length=32, choices=NotificationType.choices)
    channel = models.CharField(
        max_length=16,
        choices=NotificationChannel.choices,
        default=NotificationChannel.PUSH,
    )
    status = models.CharField(
        max_length=16,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
        db_index=True,
    )
    title = models.CharField(max_length=150)
    body = models.TextField(blank=True)
    payload = models.JSONField(default=dict, blank=True)
    resource = models.CharField(max_length=100, blank=True)
    resource_id = models.CharField(max_length=64, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["recipient", "status", "created_at"]),
            models.Index(fields=["notification_type", "created_at"]),
            models.Index(fields=["resource", "resource_id"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Return a readable notification label."""
        return f"Notification<{self.recipient_id}:{self.notification_type}>"
