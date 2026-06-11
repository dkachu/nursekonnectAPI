"""Patient dependent services."""

from __future__ import annotations

from typing import Any

from rest_framework.exceptions import PermissionDenied

from apps.patients.models import PatientDependent, PatientProfile


class PatientDependentService:
    """Manage patient dependents."""

    def create(
        self,
        *,
        actor: object,
        patient: PatientProfile,
        data: dict[str, Any],
    ) -> PatientDependent:
        """Create a dependent for the actor's own patient profile."""
        self._require_owner(actor=actor, patient=patient)
        return PatientDependent.objects.create(patient=patient, **data)

    def update(
        self,
        *,
        actor: object,
        patient: PatientProfile,
        dependent: PatientDependent,
        data: dict[str, Any],
    ) -> PatientDependent:
        """Update an owned dependent."""
        self._require_owner(actor=actor, patient=patient)
        for field, value in data.items():
            setattr(dependent, field, value)
        dependent.save()
        return dependent

    def delete(
        self,
        *,
        actor: object,
        patient: PatientProfile,
        dependent: PatientDependent,
    ) -> None:
        """Delete an owned dependent."""
        self._require_owner(actor=actor, patient=patient)
        dependent.delete()

    def _require_owner(self, *, actor: object, patient: PatientProfile) -> None:
        """Ensure the actor owns the patient profile."""
        if patient.user_id != getattr(actor, "id", None):
            raise PermissionDenied("You can manage only your own dependents.")
