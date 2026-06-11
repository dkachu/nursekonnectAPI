"""Care request domain models."""

from __future__ import annotations

from django.contrib.gis.db import models as gis_models
from django.db import models

from apps.common.models import SoftDeleteModel, TimeStampedModel


class CareRequestStatus(models.TextChoices):
    """Care request lifecycle statuses."""

    PENDING = "PENDING", "Pending"
    ACCEPTED = "ACCEPTED", "Accepted"
    PREPARING = "PREPARING", "Preparing"
    NURSE_EN_ROUTE = "NURSE_EN_ROUTE", "Nurse en route"
    ARRIVED = "ARRIVED", "Arrived"
    IN_PROGRESS = "IN_PROGRESS", "In progress"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"
    EXPIRED = "EXPIRED", "Expired"


class CareRequestPriority(models.TextChoices):
    """Care request priority levels."""

    NORMAL = "NORMAL", "Normal"
    URGENT = "URGENT", "Urgent"
    CRITICAL = "CRITICAL", "Critical"


class CareServiceType(models.TextChoices):
    """Supported home-based care service types."""

    GENERAL_NURSING = "GENERAL_NURSING", "General nursing"
    WOUND_CARE = "WOUND_CARE", "Wound care"
    ELDERLY_CARE = "ELDERLY_CARE", "Elderly care"
    PALLIATIVE_CARE = "PALLIATIVE_CARE", "Palliative care"
    POST_SURGERY_CARE = "POST_SURGERY_CARE", "Post-surgery care"
    MATERNITY_CARE = "MATERNITY_CARE", "Maternity care"
    CHRONIC_DISEASE_SUPPORT = "CHRONIC_DISEASE_SUPPORT", "Chronic disease support"


class CareRequest(TimeStampedModel, SoftDeleteModel):
    """Patient-created home care request."""

    patient = models.ForeignKey(
        "patients.PatientProfile",
        on_delete=models.PROTECT,
        related_name="care_requests",
    )
    dependent = models.ForeignKey(
        "patients.PatientDependent",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="care_requests",
    )
    service_type = models.CharField(max_length=32, choices=CareServiceType.choices)
    priority = models.CharField(
        max_length=16,
        choices=CareRequestPriority.choices,
        default=CareRequestPriority.NORMAL,
    )
    description = models.TextField(blank=True)
    location = gis_models.PointField(
        geography=True,
        srid=4326,
        spatial_index=True,
    )
    requested_time = models.DateTimeField()
    status = models.CharField(
        max_length=16,
        choices=CareRequestStatus.choices,
        default=CareRequestStatus.PENDING,
        db_index=True,
    )
    assigned_nurse = models.ForeignKey(
        "nurses.NurseProfile",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="assigned_care_requests",
    )
    accepted_at = models.DateTimeField(blank=True, null=True)
    journey_started_at = models.DateTimeField(blank=True, null=True)
    arrived_at = models.DateTimeField(blank=True, null=True)
    visit_started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    expired_at = models.DateTimeField(blank=True, null=True)
    cancellation_reason = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["patient", "status"]),
            models.Index(fields=["assigned_nurse", "status"]),
            models.Index(fields=["status", "priority", "created_at"]),
            models.Index(fields=["requested_time"]),
            models.Index(fields=["is_deleted", "deleted_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Return a readable care request label."""
        return f"CareRequest<{self.id}:{self.status}>"


class RequestOfferStatus(models.TextChoices):
    """Request offer lifecycle statuses."""

    OFFERED = "OFFERED", "Offered"
    ACCEPTED = "ACCEPTED", "Accepted"
    EXPIRED = "EXPIRED", "Expired"
    CANCELLED = "CANCELLED", "Cancelled"


class RequestOffer(TimeStampedModel):
    """Notification offer sent to an eligible nurse for a care request."""

    care_request = models.ForeignKey(
        CareRequest,
        on_delete=models.CASCADE,
        related_name="offers",
    )
    nurse = models.ForeignKey(
        "nurses.NurseProfile",
        on_delete=models.PROTECT,
        related_name="request_offers",
    )
    status = models.CharField(
        max_length=16,
        choices=RequestOfferStatus.choices,
        default=RequestOfferStatus.OFFERED,
        db_index=True,
    )
    radius_km = models.PositiveSmallIntegerField()
    distance_km = models.DecimalField(max_digits=6, decimal_places=2)
    estimated_travel_time = models.PositiveSmallIntegerField()
    specialization_match = models.BooleanField(default=False)
    rank = models.PositiveSmallIntegerField()
    expires_at = models.DateTimeField()
    notification = models.ForeignKey(
        "notifications.Notification",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="request_offers",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["care_request", "nurse"],
                name="unique_request_offer_per_nurse",
            ),
        ]
        indexes = [
            models.Index(fields=["care_request", "status"]),
            models.Index(fields=["nurse", "status"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["radius_km", "rank"]),
        ]
        ordering = ["rank", "created_at"]

    def __str__(self) -> str:
        """Return a readable request offer label."""
        return f"RequestOffer<{self.care_request_id}:{self.nurse_id}:{self.status}>"
