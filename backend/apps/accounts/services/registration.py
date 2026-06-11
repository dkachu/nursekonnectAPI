"""Registration workflow service."""

from __future__ import annotations

from dataclasses import dataclass

from django.db import transaction

from apps.accounts.models import User, UserRole
from apps.accounts.services.verification import OTPService
from apps.nurses.models import NurseProfile
from apps.patients.models import PatientProfile


@dataclass(frozen=True)
class RegistrationInput:
    """Validated registration data."""

    email: str
    password: str
    first_name: str
    last_name: str
    phone_number: str
    role: str


class RegistrationService:
    """Create users and their role-specific profiles."""

    allowed_public_roles = {UserRole.PATIENT, UserRole.NURSE}

    def __init__(self, otp_service: OTPService | None = None) -> None:
        """Initialize the registration service."""
        self.otp_service = otp_service or OTPService()

    @transaction.atomic
    def register(self, data: RegistrationInput) -> User:
        """Register a patient or nurse and create verification OTPs."""
        if data.role not in self.allowed_public_roles:
            raise ValueError("Only patient and nurse self-registration is allowed.")

        user = User.objects.create_user(
            email=data.email,
            password=data.password,
            first_name=data.first_name,
            last_name=data.last_name,
            role=data.role,
            is_active=True,
            email_verified=False,
            phone_verified=False,
        )

        if data.role == UserRole.PATIENT:
            PatientProfile.objects.create(user=user, phone_number=data.phone_number)
        if data.role == UserRole.NURSE:
            NurseProfile.objects.create(user=user, phone_number=data.phone_number)

        self.otp_service.create_otp(user=user, purpose="EMAIL")
        self.otp_service.create_otp(user=user, purpose="PHONE")
        return user
