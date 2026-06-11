"""Nurse specialization service operations."""

from __future__ import annotations

from django.db import transaction

from apps.nurses.models import NurseProfile, NurseSpecialization


class NurseSpecializationService:
    """Manage specializations for nurse profiles."""

    @transaction.atomic
    def set_specializations(
        self,
        *,
        actor: object,
        nurse: NurseProfile,
        codes: list[str],
    ) -> NurseProfile:
        """Replace a nurse's specialization set."""
        if nurse.user_id != getattr(actor, "id", None):
            raise PermissionError("You can only update your own specializations.")
        specializations = list(NurseSpecialization.objects.filter(code__in=codes))
        if len(specializations) != len(set(codes)):
            raise ValueError("One or more specializations are not supported.")
        nurse.specializations.set(specializations)
        nurse.save(update_fields=["updated_at"])
        return nurse
