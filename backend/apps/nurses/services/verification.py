"""NCK verification service operations."""

from __future__ import annotations

from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import UserRole
from apps.nurses.models import NurseProfile, NurseVerificationStatus
from apps.nurses.services.status import NurseStatusService


class NurseVerificationService:
    """Apply administrator-controlled NCK verification decisions."""

    @transaction.atomic
    def update_verification(
        self,
        *,
        actor: object,
        nurse: NurseProfile,
        data: dict[str, Any],
    ) -> NurseProfile:
        """Update NCK verification state for a nurse."""
        if getattr(actor, "role", None) != UserRole.ADMIN or not getattr(actor, "is_staff", False):
            raise PermissionError("Only authorized administrators can verify nurses.")

        status = data["nck_verification_status"]
        expiry = data.get("nck_license_expiry", nurse.nck_license_expiry)
        license_number = data.get("nck_license_number", nurse.nck_license_number)
        if status == NurseVerificationStatus.VERIFIED:
            if not license_number:
                raise ValueError("NCK license number is required for verification.")
            if expiry is None or expiry < timezone.localdate():
                raise ValueError("A future NCK license expiry is required for verification.")

        for field, value in data.items():
            setattr(nurse, field, value)
        nurse.save(update_fields=[*data.keys(), "updated_at"])
        NurseStatusService().refresh_platform_availability(nurse)
        nurse.refresh_from_db()
        return nurse
