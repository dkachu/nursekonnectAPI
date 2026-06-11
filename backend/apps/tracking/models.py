"""Tracking domain models."""

from __future__ import annotations

from django.contrib.gis.db import models as gis_models
from django.db import models

from apps.common.models import TimeStampedModel
from apps.nurses.models import NurseProfile


class TrackingLocation(TimeStampedModel):
    """GPS point emitted by a nurse device during journey tracking."""

    nurse = models.ForeignKey(
        NurseProfile,
        on_delete=models.CASCADE,
        related_name="tracking_locations",
    )
    care_request = models.ForeignKey(
        "requests.CareRequest",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="tracking_locations",
    )
    location = gis_models.PointField(
        geography=True,
        srid=4326,
        spatial_index=True,
    )
    recorded_at = models.DateTimeField()
    accuracy_meters = models.PositiveSmallIntegerField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["nurse", "recorded_at"]),
            models.Index(fields=["care_request", "recorded_at"]),
            models.Index(fields=["recorded_at"]),
        ]
        ordering = ["-recorded_at"]

    def __str__(self) -> str:
        """Return a readable tracking location label."""
        return f"TrackingLocation<{self.nurse_id}:{self.recorded_at.isoformat()}>"
