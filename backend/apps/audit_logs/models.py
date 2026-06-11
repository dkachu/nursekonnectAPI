"""Audit log domain models."""

from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class MedicalAccessLog(TimeStampedModel):
    """Append-only record of protected medical data access."""

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="medical_access_logs",
    )
    patient = models.ForeignKey(
        "patients.PatientProfile",
        on_delete=models.PROTECT,
        related_name="medical_access_logs",
    )
    resource = models.CharField(max_length=100)
    resource_id = models.CharField(max_length=64)
    action = models.CharField(max_length=64)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["actor", "created_at"]),
            models.Index(fields=["patient", "created_at"]),
            models.Index(fields=["resource", "resource_id"]),
        ]

    def __str__(self) -> str:
        """Return a readable log label."""
        return f"MedicalAccessLog<{self.actor_id}:{self.patient_id}:{self.resource}>"
