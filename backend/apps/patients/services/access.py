"""Patient medical-data access policy."""

from __future__ import annotations

from apps.accounts.models import UserRole
from apps.patients.models import PatientProfile


class PatientMedicalAccessService:
    """Authorize protected medical-data access."""

    def can_access_medical_data(self, *, actor: object, patient: PatientProfile) -> bool:
        """Return whether actor may access protected patient medical data."""
        if not getattr(actor, "is_authenticated", False):
            return False
        if getattr(actor, "role", None) == UserRole.PATIENT:
            return patient.user_id == actor.id
        if getattr(actor, "role", None) == UserRole.ADMIN:
            return bool(getattr(actor, "is_staff", False))
        if getattr(actor, "role", None) == UserRole.NURSE:
            return self.has_assigned_patient_access(actor=actor, patient=patient)
        return False

    def has_assigned_patient_access(self, *, actor: object, patient: PatientProfile) -> bool:
        """Return whether a nurse is assigned to an active or completed patient request."""
        from apps.requests.models import CareRequest, CareRequestStatus

        return (
            CareRequest.objects.filter(
                patient=patient,
                assigned_nurse__user=actor,
            )
            .exclude(status__in=[CareRequestStatus.CANCELLED, CareRequestStatus.EXPIRED])
            .exists()
        )
