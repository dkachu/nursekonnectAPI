"""Emergency contact services."""

from __future__ import annotations

from typing import Any

from rest_framework.exceptions import PermissionDenied

from apps.patients.models import EmergencyContact, PatientProfile


class EmergencyContactService:
    """Manage patient emergency contacts."""

    def create(
        self,
        *,
        actor: object,
        patient: PatientProfile,
        data: dict[str, Any],
    ) -> EmergencyContact:
        """Create an emergency contact for the actor's own patient profile."""
        self._require_owner(actor=actor, patient=patient)
        return EmergencyContact.objects.create(patient=patient, **data)

    def update(
        self,
        *,
        actor: object,
        patient: PatientProfile,
        contact: EmergencyContact,
        data: dict[str, Any],
    ) -> EmergencyContact:
        """Update an owned emergency contact."""
        self._require_owner(actor=actor, patient=patient)
        for field, value in data.items():
            setattr(contact, field, value)
        contact.save()
        return contact

    def delete(self, *, actor: object, patient: PatientProfile, contact: EmergencyContact) -> None:
        """Delete an owned emergency contact."""
        self._require_owner(actor=actor, patient=patient)
        contact.delete()

    def _require_owner(self, *, actor: object, patient: PatientProfile) -> None:
        """Ensure the actor owns the patient profile."""
        if patient.user_id != getattr(actor, "id", None):
            raise PermissionDenied("You can manage only your own emergency contacts.")
