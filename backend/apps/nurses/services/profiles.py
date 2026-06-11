"""Nurse profile service operations."""

from __future__ import annotations

from typing import Any

from django.db import transaction

from apps.nurses.models import NurseProfile
from apps.nurses.services.status import NurseStatusService


class NurseProfileService:
    """Apply nurse profile updates."""

    @transaction.atomic
    def update_own_profile(
        self,
        *,
        actor: object,
        nurse: NurseProfile,
        data: dict[str, Any],
    ) -> NurseProfile:
        """Update a nurse-owned profile."""
        if nurse.user_id != getattr(actor, "id", None):
            raise PermissionError("You can only update your own nurse profile.")

        for field, value in data.items():
            setattr(nurse, field, value)
        nurse.save(update_fields=[*data.keys(), "updated_at"])
        NurseStatusService().refresh_platform_availability(nurse)
        nurse.refresh_from_db()
        return nurse
