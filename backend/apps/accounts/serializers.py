"""Authentication serializers."""

from __future__ import annotations

from typing import Any

from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from rest_framework import serializers

from apps.accounts.models import OTPPurpose, User, UserRole

phone_validator = RegexValidator(
    regex=r"^\+254\d{9}$",
    message="Phone number must use Kenyan E.164 format, for example +254712345678.",
)


class UserSerializer(serializers.ModelSerializer[User]):
    """Public authenticated user payload."""

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "email_verified",
            "phone_verified",
        )
        read_only_fields = fields


class RegisterSerializer(serializers.Serializer[dict[str, Any]]):
    """Validate registration input."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    phone_number = serializers.CharField(validators=[phone_validator])
    role = serializers.ChoiceField(choices=[UserRole.PATIENT, UserRole.NURSE])

    def validate_password(self, value: str) -> str:
        """Apply Django password validators."""
        validate_password(value)
        return value

    def validate_email(self, value: str) -> str:
        """Normalize email input."""
        normalized = User.objects.normalize_email(value)
        if User.objects.filter(email__iexact=normalized).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return normalized


class LoginSerializer(serializers.Serializer[dict[str, str]]):
    """Validate login credentials."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_email(self, value: str) -> str:
        """Normalize email input."""
        return User.objects.normalize_email(value)


class RefreshSerializer(serializers.Serializer[dict[str, str]]):
    """Validate refresh token input."""

    refresh = serializers.CharField()


class LogoutSerializer(serializers.Serializer[dict[str, str]]):
    """Validate logout token input."""

    refresh = serializers.CharField()


class OTPVerifySerializer(serializers.Serializer[dict[str, str]]):
    """Validate OTP verification input."""

    purpose = serializers.ChoiceField(choices=OTPPurpose.values)
    code = serializers.CharField(min_length=6, max_length=6)


class OTPResendSerializer(serializers.Serializer[dict[str, str]]):
    """Validate OTP resend input."""

    purpose = serializers.ChoiceField(choices=OTPPurpose.values)
