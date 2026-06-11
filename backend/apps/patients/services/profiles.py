"""Patient profile services."""

from __future__ import annotations

from typing import Any

from rest_framework.exceptions import PermissionDenied

from apps.audit_logs.services.medical_access import MedicalAccessLogService
from apps.patients.models import PatientProfile
from apps.patients.services.access import PatientMedicalAccessService


class PatientProfileService:
    """Manage patient profile reads and updates."""

    protected_resource = "PatientProfile.medical_information"

    def __init__(
        self,
        access_service: PatientMedicalAccessService | None = None,
        log_service: MedicalAccessLogService | None = None,
    ) -> None:
        """Initialize the profile service."""
        self.access_service = access_service or PatientMedicalAccessService()
        self.log_service = log_service or MedicalAccessLogService()

    def read_profile(
        self,
        *,
        actor: object,
        patient: PatientProfile,
        ip_address: str | None,
        include_medical: bool,
    ) -> PatientProfile:
        """Authorize and log patient profile access."""
        is_owner = patient.user_id == getattr(actor, "id", None)
        has_medical_access = self.access_service.can_access_medical_data(
            actor=actor,
            patient=patient,
        )
        if not is_owner and not has_medical_access:
            raise PermissionDenied("You do not have access to this patient profile.")
        if include_medical:
            self._authorize_and_log_medical_access(
                actor=actor,
                patient=patient,
                ip_address=ip_address,
            )
        return patient

    def update_own_profile(
        self,
        *,
        actor: object,
        patient: PatientProfile,
        data: dict[str, Any],
    ) -> PatientProfile:
        """Update the authenticated patient's own profile."""
        if patient.user_id != getattr(actor, "id", None):
            raise PermissionDenied("You can update only your own patient profile.")
        for field, value in data.items():
            setattr(patient, field, value)
        patient.save()
        return patient

    def read_medical_information(
        self,
        *,
        actor: object,
        patient: PatientProfile,
        ip_address: str | None,
    ) -> PatientProfile:
        """Authorize and log protected medical information access."""
        self._authorize_and_log_medical_access(actor=actor, patient=patient, ip_address=ip_address)
        return patient

    def _authorize_and_log_medical_access(
        self,
        *,
        actor: object,
        patient: PatientProfile,
        ip_address: str | None,
    ) -> None:
        """Authorize protected medical data access and create a log record."""
        if not self.access_service.can_access_medical_data(actor=actor, patient=patient):
            raise PermissionDenied("You do not have access to this patient's medical information.")
        self.log_service.record(
            actor=actor,
            patient=patient,
            resource=self.protected_resource,
            resource_id=patient.id,
            action="READ",
            ip_address=ip_address,
        )
