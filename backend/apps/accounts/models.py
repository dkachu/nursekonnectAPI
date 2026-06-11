"""Custom email-only user model."""

from __future__ import annotations

from typing import Any

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone

from apps.common.models import TimeStampedModel


class UserRole(models.TextChoices):
    """Supported platform roles."""

    PATIENT = "PATIENT", "Patient"
    NURSE = "NURSE", "Nurse"
    ADMIN = "ADMIN", "Administrator"


class UserManager(BaseUserManager["User"]):
    """Manager for email-only users."""

    use_in_migrations = True

    def create_user(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: Any,
    ) -> User:
        """Create a regular user with a normalized email address."""
        if not email:
            raise ValueError("An email address is required.")

        normalized_email = self.normalize_email(email)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        user = self.model(email=normalized_email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: Any,
    ) -> User:
        """Create a superuser for administrative access."""
        extra_fields.setdefault("role", UserRole.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("email_verified", True)
        extra_fields.setdefault("phone_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if extra_fields.get("role") != UserRole.ADMIN:
            raise ValueError("Superuser must have role=ADMIN.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """Central account model for patients, nurses, and administrators."""

    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    role = models.CharField(max_length=16, choices=UserRole.choices)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        ordering = ["email"]

    def __str__(self) -> str:
        """Return the user's email address."""
        return self.email

    @property
    def full_name(self) -> str:
        """Return the display name assembled from first and last name."""
        return f"{self.first_name} {self.last_name}".strip()


class OTPPurpose(models.TextChoices):
    """Supported verification OTP purposes."""

    EMAIL = "EMAIL", "Email verification"
    PHONE = "PHONE", "Phone verification"


class AuthenticationOTP(TimeStampedModel):
    """Hashed one-time password for email or phone verification."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="authentication_otps",
    )
    purpose = models.CharField(max_length=16, choices=OTPPurpose.choices)
    code_hash = models.CharField(max_length=128)
    expires_at = models.DateTimeField()
    consumed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "purpose", "expires_at"]),
        ]
        ordering = ["-created_at"]

    @property
    def is_consumed(self) -> bool:
        """Return whether the OTP has already been consumed."""
        return self.consumed_at is not None

    @property
    def is_expired(self) -> bool:
        """Return whether the OTP has expired."""
        return timezone.now() >= self.expires_at
