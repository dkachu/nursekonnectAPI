"""Medical access logging service."""

from __future__ import annotations

from apps.audit_logs.models import MedicalAccessLog
from apps.patients.models import PatientProfile


class MedicalAccessLogService:
    """Persist medical access logs for protected patient data reads."""

    def record(
        self,
        *,
        actor: object,
        patient: PatientProfile,
        resource: str,
        resource_id: str | int,
        action: str,
        ip_address: str | None,
    ) -> MedicalAccessLog:
        """Create a medical access log entry."""
        return MedicalAccessLog.objects.create(
            actor=actor,
            patient=patient,
            resource=resource,
            resource_id=str(resource_id),
            action=action,
            ip_address=ip_address,
        )
