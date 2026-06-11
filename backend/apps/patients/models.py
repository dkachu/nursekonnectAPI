"""Patient domain models."""

from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.fields import EncryptedTextField
from apps.common.models import TimeStampedModel


class Gender(models.TextChoices):
    """Supported gender values."""

    FEMALE = "FEMALE", "Female"
    MALE = "MALE", "Male"
    OTHER = "OTHER", "Other"
    UNDISCLOSED = "UNDISCLOSED", "Undisclosed"


class BloodGroup(models.TextChoices):
    """Supported blood groups."""

    A_POSITIVE = "A+", "A+"
    A_NEGATIVE = "A-", "A-"
    B_POSITIVE = "B+", "B+"
    B_NEGATIVE = "B-", "B-"
    AB_POSITIVE = "AB+", "AB+"
    AB_NEGATIVE = "AB-", "AB-"
    O_POSITIVE = "O+", "O+"
    O_NEGATIVE = "O-", "O-"
    UNKNOWN = "UNKNOWN", "Unknown"


class PatientProfile(TimeStampedModel):
    """Patient-specific profile linked to the central user model."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patient_profile",
    )
    phone_number = models.CharField(max_length=20)
    national_id = models.CharField(max_length=32, blank=True)
    gender = models.CharField(max_length=16, choices=Gender.choices, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_photo = models.FileField(upload_to="patient_profiles/", blank=True)
    blood_group = models.CharField(
        max_length=8,
        choices=BloodGroup.choices,
        default=BloodGroup.UNKNOWN,
    )
    allergies = EncryptedTextField(blank=True, default="")
    chronic_conditions = EncryptedTextField(blank=True, default="")
    current_medications = EncryptedTextField(blank=True, default="")
    disabilities = models.TextField(blank=True)
    medical_notes = EncryptedTextField(blank=True, default="")
    county = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)

    class Meta:
        ordering = ["user__email"]

    def __str__(self) -> str:
        """Return a readable patient profile label."""
        return f"PatientProfile<{self.user_id}>"


class EmergencyContact(TimeStampedModel):
    """Emergency contact for a patient."""

    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name="emergency_contacts",
    )
    name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20)
    relationship = models.CharField(max_length=64)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        """Return a readable emergency contact label."""
        return f"EmergencyContact<{self.patient_id}:{self.name}>"


class PatientDependent(TimeStampedModel):
    """Dependent who can receive care under a patient account."""

    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name="dependents",
    )
    full_name = models.CharField(max_length=150)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=16, choices=Gender.choices)
    relationship = models.CharField(max_length=64)
    medical_notes = EncryptedTextField(blank=True, default="")

    class Meta:
        ordering = ["full_name"]

    def __str__(self) -> str:
        """Return a readable dependent label."""
        return f"PatientDependent<{self.patient_id}:{self.full_name}>"
