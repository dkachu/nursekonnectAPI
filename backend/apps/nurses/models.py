"""Nurse domain models."""

from __future__ import annotations

from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils import timezone

from apps.common.models import TimeStampedModel
from apps.patients.models import Gender


class NurseVerificationStatus(models.TextChoices):
    """NCK verification states for nurses."""

    PENDING = "PENDING", "Pending"
    UNDER_REVIEW = "UNDER_REVIEW", "Under review"
    VERIFIED = "VERIFIED", "Verified"
    REJECTED = "REJECTED", "Rejected"
    EXPIRED = "EXPIRED", "Expired"


class NurseStatus(models.TextChoices):
    """Operational nurse availability state."""

    ONLINE = "ONLINE", "Online"
    BUSY = "BUSY", "Busy"
    OFFLINE = "OFFLINE", "Offline"


class NurseSpecializationCode(models.TextChoices):
    """Supported nurse specialization codes."""

    GENERAL_NURSING = "GENERAL_NURSING", "General nursing"
    WOUND_CARE = "WOUND_CARE", "Wound care"
    GERIATRIC_CARE = "GERIATRIC_CARE", "Geriatric care"
    PALLIATIVE_CARE = "PALLIATIVE_CARE", "Palliative care"
    PEDIATRIC_CARE = "PEDIATRIC_CARE", "Pediatric care"
    MIDWIFERY = "MIDWIFERY", "Midwifery"
    MENTAL_HEALTH = "MENTAL_HEALTH", "Mental health"
    ICU_CARE = "ICU_CARE", "ICU care"
    POST_SURGICAL_CARE = "POST_SURGICAL_CARE", "Post-surgical care"
    CHRONIC_DISEASE_SUPPORT = "CHRONIC_DISEASE_SUPPORT", "Chronic disease support"


class TravelRadiusKm(models.IntegerChoices):
    """Allowed maximum travel radius values."""

    TEN = 10, "10km"
    TWENTY = 20, "20km"
    FIFTY = 50, "50km"
    HUNDRED = 100, "100km"


class CredentialType(models.TextChoices):
    """Supported nurse credential document types."""

    NCK_LICENSE = "NCK_LICENSE", "NCK license"
    NATIONAL_ID = "NATIONAL_ID", "National ID"
    PASSPORT_PHOTO = "PASSPORT_PHOTO", "Passport photo"
    ACADEMIC_CERTIFICATE = "ACADEMIC_CERTIFICATE", "Academic certificate"
    PROFESSIONAL_CERTIFICATE = "PROFESSIONAL_CERTIFICATE", "Professional certificate"


class DayOfWeek(models.IntegerChoices):
    """ISO weekday values for nurse availability."""

    MONDAY = 1, "Monday"
    TUESDAY = 2, "Tuesday"
    WEDNESDAY = 3, "Wednesday"
    THURSDAY = 4, "Thursday"
    FRIDAY = 5, "Friday"
    SATURDAY = 6, "Saturday"
    SUNDAY = 7, "Sunday"


class NurseSpecialization(TimeStampedModel):
    """Catalog entry for a nurse specialization."""

    code = models.CharField(
        max_length=32,
        choices=NurseSpecializationCode.choices,
        unique=True,
        db_index=True,
    )
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["code"]

    def __str__(self) -> str:
        """Return the specialization code."""
        return self.code


class NurseProfile(TimeStampedModel):
    """Nurse-specific profile linked to the central user model."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="nurse_profile",
    )
    phone_number = models.CharField(max_length=20)
    national_id = models.CharField(max_length=32, blank=True)
    gender = models.CharField(max_length=16, choices=Gender.choices, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_photo = models.ImageField(upload_to="nurse_profiles/", blank=True)
    nck_license_number = models.CharField(max_length=64, blank=True, db_index=True)
    nck_license_expiry = models.DateField(blank=True, null=True)
    nck_verification_status = models.CharField(
        max_length=16,
        choices=NurseVerificationStatus.choices,
        default=NurseVerificationStatus.PENDING,
    )
    specializations = models.ManyToManyField(
        NurseSpecialization,
        blank=True,
        related_name="nurses",
    )
    years_of_experience = models.PositiveSmallIntegerField(default=0)
    bio = models.TextField(blank=True)
    county = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    current_location = gis_models.PointField(
        geography=True,
        srid=4326,
        spatial_index=True,
        blank=True,
        null=True,
    )
    last_location_update = models.DateTimeField(blank=True, null=True)
    location_visible = models.BooleanField(default=False)
    status = models.CharField(
        max_length=16,
        choices=NurseStatus.choices,
        default=NurseStatus.OFFLINE,
    )
    is_available = models.BooleanField(default=False)
    travel_radius_km = models.PositiveSmallIntegerField(
        choices=TravelRadiusKm.choices,
        default=TravelRadiusKm.TEN,
    )
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    completed_visits_count = models.PositiveIntegerField(default=0)
    cancelled_visits_count = models.PositiveIntegerField(default=0)
    average_response_seconds = models.PositiveIntegerField(default=0)
    reputation_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        indexes = [
            models.Index(fields=["nck_verification_status", "status", "is_available"]),
            models.Index(fields=["travel_radius_km"]),
            models.Index(fields=["last_location_update"]),
        ]
        ordering = ["user__email"]

    @property
    def license_is_expired(self) -> bool:
        """Return whether the NCK license has expired."""
        return bool(self.nck_license_expiry and self.nck_license_expiry < timezone.localdate())

    def __str__(self) -> str:
        """Return a readable nurse profile label."""
        return f"NurseProfile<{self.user_id}>"


class NurseCredential(TimeStampedModel):
    """Uploaded nurse credential image."""

    nurse = models.ForeignKey(
        NurseProfile,
        on_delete=models.CASCADE,
        related_name="credentials",
    )
    credential_type = models.CharField(max_length=32, choices=CredentialType.choices)
    image = models.ImageField(upload_to="nurse_credentials/")
    verification_status = models.CharField(
        max_length=16,
        choices=NurseVerificationStatus.choices,
        default=NurseVerificationStatus.PENDING,
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="reviewed_nurse_credentials",
    )
    reviewed_at = models.DateTimeField(blank=True, null=True)
    review_notes = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["nurse", "credential_type"]),
            models.Index(fields=["verification_status"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Return a readable credential label."""
        return f"NurseCredential<{self.nurse_id}:{self.credential_type}>"


class NurseAvailabilitySlot(TimeStampedModel):
    """Recurring weekly availability window for a nurse."""

    nurse = models.ForeignKey(
        NurseProfile,
        on_delete=models.CASCADE,
        related_name="availability_slots",
    )
    day_of_week = models.PositiveSmallIntegerField(choices=DayOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(start_time__lt=models.F("end_time")),
                name="nurse_availability_start_before_end",
            ),
            models.UniqueConstraint(
                fields=["nurse", "day_of_week", "start_time", "end_time"],
                name="unique_nurse_availability_slot",
            ),
        ]
        indexes = [
            models.Index(fields=["nurse", "day_of_week"]),
        ]
        ordering = ["day_of_week", "start_time"]

    def __str__(self) -> str:
        """Return a readable availability label."""
        return f"NurseAvailabilitySlot<{self.nurse_id}:{self.day_of_week}>"
