"""Nurse availability service operations."""

from __future__ import annotations

from typing import Any

from django.db import transaction

from apps.nurses.models import NurseAvailabilitySlot, NurseProfile


class NurseAvailabilityService:
    """Manage recurring nurse availability slots."""

    @transaction.atomic
    def create(
        self,
        *,
        actor: object,
        nurse: NurseProfile,
        data: dict[str, Any],
    ) -> NurseAvailabilitySlot:
        """Create an availability slot for a nurse."""
        self._ensure_owner(actor=actor, nurse=nurse)
        return NurseAvailabilitySlot.objects.create(nurse=nurse, **data)

    @transaction.atomic
    def update(
        self,
        *,
        actor: object,
        nurse: NurseProfile,
        slot: NurseAvailabilitySlot,
        data: dict[str, Any],
    ) -> NurseAvailabilitySlot:
        """Update an availability slot."""
        self._ensure_owner(actor=actor, nurse=nurse)
        if slot.nurse_id != nurse.id:
            raise PermissionError("You can only update your own availability slots.")
        for field, value in data.items():
            setattr(slot, field, value)
        slot.save(update_fields=[*data.keys(), "updated_at"])
        return slot

    @transaction.atomic
    def delete(self, *, actor: object, nurse: NurseProfile, slot: NurseAvailabilitySlot) -> None:
        """Delete an availability slot."""
        self._ensure_owner(actor=actor, nurse=nurse)
        if slot.nurse_id != nurse.id:
            raise PermissionError("You can only delete your own availability slots.")
        slot.delete()

    def _ensure_owner(self, *, actor: object, nurse: NurseProfile) -> None:
        """Validate that the actor owns the nurse profile."""
        if nurse.user_id != getattr(actor, "id", None):
            raise PermissionError("You can only manage your own availability.")
