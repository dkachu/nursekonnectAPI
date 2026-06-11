"""OTP verification service."""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import timedelta

from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import AuthenticationOTP, OTPPurpose, User


@dataclass(frozen=True)
class OTPResult:
    """OTP creation result."""

    code: str
    expires_at: object


class OTPService:
    """Create, resend, and verify one-time passwords."""

    code_length = 6
    lifetime = timedelta(minutes=10)

    def create_otp(self, user: User, purpose: str) -> OTPResult:
        """Create a hashed OTP for a user and purpose."""
        normalized_purpose = self._normalize_purpose(purpose)
        code = f"{secrets.randbelow(10**self.code_length):0{self.code_length}d}"
        expires_at = timezone.now() + self.lifetime
        AuthenticationOTP.objects.create(
            user=user,
            purpose=normalized_purpose,
            code_hash=make_password(code),
            expires_at=expires_at,
        )
        return OTPResult(code=code, expires_at=expires_at)

    def resend_otp(self, user: User, purpose: str) -> OTPResult:
        """Create a replacement OTP for the user and purpose."""
        normalized_purpose = self._normalize_purpose(purpose)
        AuthenticationOTP.objects.filter(
            user=user,
            purpose=normalized_purpose,
            consumed_at__isnull=True,
        ).update(consumed_at=timezone.now())
        return self.create_otp(user=user, purpose=normalized_purpose)

    @transaction.atomic
    def verify_otp(self, user: User, purpose: str, code: str) -> User:
        """Verify an OTP and update the user's verification flag."""
        normalized_purpose = self._normalize_purpose(purpose)
        otp = (
            AuthenticationOTP.objects.select_for_update()
            .filter(user=user, purpose=normalized_purpose, consumed_at__isnull=True)
            .order_by("-created_at")
            .first()
        )
        if otp is None or otp.is_expired or not check_password(code, otp.code_hash):
            raise ValueError("Invalid or expired OTP.")

        otp.consumed_at = timezone.now()
        otp.save(update_fields=["consumed_at", "updated_at"])

        if normalized_purpose == OTPPurpose.EMAIL:
            user.email_verified = True
            user.save(update_fields=["email_verified", "updated_at"])
        if normalized_purpose == OTPPurpose.PHONE:
            user.phone_verified = True
            user.save(update_fields=["phone_verified", "updated_at"])
        return user

    def _normalize_purpose(self, purpose: str) -> str:
        """Validate and normalize an OTP purpose."""
        normalized = purpose.upper()
        if normalized not in OTPPurpose.values:
            raise ValueError("Unsupported OTP purpose.")
        return normalized
