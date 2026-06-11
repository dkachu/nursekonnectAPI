"""Nurse status and platform availability services."""

from __future__ import annotations

from django.db import transaction

from apps.nurses.models import NurseProfile, NurseStatus, NurseVerificationStatus


class NurseStatusService:
    """Manage nurse online status and availability gates."""

    @transaction.atomic
    def update_status(
        self,
        *,
        actor: object,
        nurse: NurseProfile,
        status: str,
        location_visible: bool | None = None,
    ) -> NurseProfile:
        """Update a nurse's operational status."""
        if nurse.user_id != getattr(actor, "id", None):
            raise PermissionError("You can only update your own nurse status.")
        if status == NurseStatus.ONLINE and not nurse.is_available:
            raise ValueError("NCK, email, and phone verification are required before going online.")

        nurse.status = status
        if location_visible is not None:
            nurse.location_visible = location_visible
        if status in {NurseStatus.BUSY, NurseStatus.OFFLINE}:
            nurse.location_visible = False
        nurse.save(update_fields=["status", "location_visible", "updated_at"])
        return nurse

    def refresh_platform_availability(self, nurse: NurseProfile) -> NurseProfile:
        """Refresh whether a nurse is eligible to receive requests."""
        can_receive_requests = (
            getattr(nurse.user, "email_verified", False)
            and getattr(nurse.user, "phone_verified", False)
            and nurse.nck_verification_status == NurseVerificationStatus.VERIFIED
            and not nurse.license_is_expired
        )
        if nurse.is_available != can_receive_requests:
            nurse.is_available = can_receive_requests
            update_fields = ["is_available", "updated_at"]
            if not can_receive_requests and nurse.status != NurseStatus.OFFLINE:
                nurse.status = NurseStatus.OFFLINE
                nurse.location_visible = False
                update_fields.extend(["status", "location_visible"])
            nurse.save(update_fields=update_fields)
        return nurse
