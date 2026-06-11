"""Optimized nurse-domain reads."""

from __future__ import annotations

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from apps.nurses.models import NurseAvailabilitySlot, NurseCredential, NurseProfile


class NurseProfileSelector:
    """Read nurse profiles with related user and specialization data."""

    def get_for_user(self, user: object) -> NurseProfile:
        """Return a nurse's own profile."""
        return get_object_or_404(
            NurseProfile.objects.select_related("user").prefetch_related("specializations"),
            user=user,
        )

    def get_by_id(self, nurse_id: int) -> NurseProfile:
        """Return a nurse profile by primary key."""
        return get_object_or_404(
            NurseProfile.objects.select_related("user").prefetch_related("specializations"),
            id=nurse_id,
        )


class NurseCredentialSelector:
    """Read nurse credentials."""

    def list_for_nurse(self, nurse: NurseProfile) -> QuerySet[NurseCredential]:
        """Return credentials uploaded by a nurse."""
        return nurse.credentials.select_related("reviewed_by")

    def get_for_nurse(self, nurse: NurseProfile, credential_id: int) -> NurseCredential:
        """Return a credential owned by a nurse."""
        return get_object_or_404(nurse.credentials.select_related("reviewed_by"), id=credential_id)


class NurseAvailabilitySelector:
    """Read nurse availability slots."""

    def list_for_nurse(self, nurse: NurseProfile) -> QuerySet[NurseAvailabilitySlot]:
        """Return availability slots for a nurse."""
        return nurse.availability_slots.all()

    def get_for_nurse(self, nurse: NurseProfile, slot_id: int) -> NurseAvailabilitySlot:
        """Return one availability slot owned by a nurse."""
        return get_object_or_404(nurse.availability_slots, id=slot_id)
