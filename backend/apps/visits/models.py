"""Visit domain models."""

from __future__ import annotations

from datetime import datetime, timedelta

from django.db import models
from django.utils import timezone

from apps.common.fields import EncryptedTextField
from apps.common.models import SoftDeleteModel, TimeStampedModel


class FollowUpSchedule(models.TextChoices):
    """Supported follow-up visit schedules."""

    ONE_DAY = "1_DAY", "1 day"
    THREE_DAYS = "3_DAYS", "3 days"
    ONE_WEEK = "1_WEEK", "1 week"
    TWO_WEEKS = "2_WEEKS", "2 weeks"
    ONE_MONTH = "1_MONTH", "1 month"


FOLLOW_UP_DELTAS: dict[str, timedelta] = {
    FollowUpSchedule.ONE_DAY: timedelta(days=1),
    FollowUpSchedule.THREE_DAYS: timedelta(days=3),
    FollowUpSchedule.ONE_WEEK: timedelta(weeks=1),
    FollowUpSchedule.TWO_WEEKS: timedelta(weeks=2),
    FollowUpSchedule.ONE_MONTH: timedelta(days=30),
}


class VisitNote(TimeStampedModel, SoftDeleteModel):
    """Protected clinical note for a completed or in-progress care visit."""

    care_request = models.OneToOneField(
        "requests.CareRequest",
        on_delete=models.PROTECT,
        related_name="visit_note",
    )
    patient = models.ForeignKey(
        "patients.PatientProfile",
        on_delete=models.PROTECT,
        related_name="visit_notes",
    )
    nurse = models.ForeignKey(
        "nurses.NurseProfile",
        on_delete=models.PROTECT,
        related_name="visit_notes",
    )
    vitals = EncryptedTextField(blank=True, default="")
    observations = EncryptedTextField(blank=True, default="")
    medication_given = EncryptedTextField(blank=True, default="")
    recommendations = EncryptedTextField(blank=True, default="")
    follow_up_required = models.BooleanField(default=False)
    follow_up_schedule = models.CharField(
        max_length=16,
        choices=FollowUpSchedule.choices,
        blank=True,
    )
    follow_up_due_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["patient", "created_at"]),
            models.Index(fields=["nurse", "created_at"]),
            models.Index(fields=["follow_up_required", "follow_up_due_at"]),
            models.Index(fields=["is_deleted", "deleted_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Return a readable visit note label."""
        return f"VisitNote<{self.care_request_id}:{self.patient_id}:{self.nurse_id}>"

    @staticmethod
    def due_at_for_schedule(schedule: str, *, start_at: datetime | None = None) -> datetime | None:
        """Return the due timestamp for a supported follow-up schedule."""
        delta = FOLLOW_UP_DELTAS.get(schedule)
        if delta is None:
            return None
        base_time = start_at or timezone.now()
        return base_time + delta
