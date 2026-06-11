"""Rating domain models."""

from __future__ import annotations

from django.db import models

from apps.common.models import SoftDeleteModel, TimeStampedModel


class Rating(TimeStampedModel, SoftDeleteModel):
    """Patient rating for a completed nurse visit."""

    patient = models.ForeignKey(
        "patients.PatientProfile",
        on_delete=models.PROTECT,
        related_name="ratings",
    )
    nurse = models.ForeignKey(
        "nurses.NurseProfile",
        on_delete=models.PROTECT,
        related_name="ratings",
    )
    care_request = models.OneToOneField(
        "requests.CareRequest",
        on_delete=models.PROTECT,
        related_name="rating",
    )
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rating__gte=1, rating__lte=5),
                name="rating_between_one_and_five",
            ),
        ]
        indexes = [
            models.Index(fields=["patient", "created_at"]),
            models.Index(fields=["nurse", "created_at"]),
            models.Index(fields=["rating"]),
            models.Index(fields=["is_deleted", "deleted_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Return a readable rating label."""
        return f"Rating<{self.patient_id}:{self.nurse_id}:{self.rating}>"
