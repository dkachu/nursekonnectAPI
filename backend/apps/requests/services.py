"""Care request service layer."""

from __future__ import annotations

from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import UserRole
from apps.audit_logs.services.audit import AuditLogService
from apps.nurses.models import NurseProfile, NurseStatus, NurseVerificationStatus
from apps.patients.models import PatientDependent, PatientProfile
from apps.requests.models import CareRequest, CareRequestStatus
from apps.requests.selectors import CareRequestSelector
from apps.tracking.services.location_updates import LocationFreshnessService

TERMINAL_STATUSES = {
    CareRequestStatus.COMPLETED,
    CareRequestStatus.CANCELLED,
    CareRequestStatus.EXPIRED,
}


class CareRequestService:
    """Create and transition care requests with audit logging."""

    def __init__(
        self,
        *,
        audit_service: AuditLogService | None = None,
        selector: CareRequestSelector | None = None,
    ) -> None:
        self.audit_service = audit_service or AuditLogService()
        self.selector = selector or CareRequestSelector()

    @transaction.atomic
    def create(
        self,
        *,
        actor: object,
        patient: PatientProfile,
        data: dict[str, Any],
        ip_address: str | None,
    ) -> CareRequest:
        """Create a care request from the patient's fresh GPS location."""
        if getattr(actor, "role", None) != UserRole.PATIENT or patient.user_id != actor.id:
            raise PermissionError("Only the patient can create their care requests.")
        if not getattr(actor, "email_verified", False) or not getattr(
            actor, "phone_verified", False
        ):
            raise ValueError("Email and phone verification are required before requesting care.")
        if patient.current_location is None or LocationFreshnessService().is_stale(
            patient.last_location_update
        ):
            raise ValueError("Fresh patient GPS location is required before requesting care.")

        dependent = self._dependent_for_patient(
            patient=patient,
            dependent_id=data.pop("dependent_id", None),
        )
        request = CareRequest.objects.create(
            patient=patient,
            dependent=dependent,
            location=patient.current_location,
            requested_time=data.get("requested_time") or timezone.now(),
            service_type=data["service_type"],
            priority=data["priority"],
            description=data.get("description", ""),
        )
        self._audit(
            actor=actor,
            action="CARE_REQUEST_CREATED",
            request=request,
            ip_address=ip_address,
        )
        return request

    @transaction.atomic
    def accept(
        self,
        *,
        actor: object,
        request_id: int,
        ip_address: str | None,
    ) -> CareRequest:
        """Atomically assign a pending care request to an eligible nurse."""
        nurse = self._locked_nurse(actor)
        self._ensure_nurse_can_accept(nurse)
        request = self.selector.get_for_update(request_id=request_id)
        if request.status != CareRequestStatus.PENDING or request.assigned_nurse_id is not None:
            raise ValueError("Care request is no longer available for acceptance.")

        now = timezone.now()
        request.assigned_nurse = nurse
        request.status = CareRequestStatus.ACCEPTED
        request.accepted_at = now
        request.save(update_fields=["assigned_nurse", "status", "accepted_at", "updated_at"])

        nurse.status = NurseStatus.BUSY
        nurse.save(update_fields=["status", "updated_at"])
        self._audit(
            actor=actor,
            action="CARE_REQUEST_ACCEPTED",
            request=request,
            ip_address=ip_address,
            metadata={"nurse_id": nurse.id},
        )
        return request

    @transaction.atomic
    def start_journey(
        self,
        *,
        actor: object,
        request_id: int,
        ip_address: str | None,
    ) -> CareRequest:
        """Move an accepted request into en-route status."""
        return self._assigned_nurse_transition(
            actor=actor,
            request_id=request_id,
            allowed_statuses={CareRequestStatus.ACCEPTED, CareRequestStatus.PREPARING},
            next_status=CareRequestStatus.NURSE_EN_ROUTE,
            timestamp_field="journey_started_at",
            action="CARE_REQUEST_JOURNEY_STARTED",
            ip_address=ip_address,
        )

    @transaction.atomic
    def mark_arrived(
        self,
        *,
        actor: object,
        request_id: int,
        ip_address: str | None,
    ) -> CareRequest:
        """Mark an en-route nurse as arrived."""
        return self._assigned_nurse_transition(
            actor=actor,
            request_id=request_id,
            allowed_statuses={CareRequestStatus.NURSE_EN_ROUTE},
            next_status=CareRequestStatus.ARRIVED,
            timestamp_field="arrived_at",
            action="CARE_REQUEST_NURSE_ARRIVED",
            ip_address=ip_address,
        )

    @transaction.atomic
    def start_visit(
        self,
        *,
        actor: object,
        request_id: int,
        ip_address: str | None,
    ) -> CareRequest:
        """Start the visit after nurse arrival."""
        return self._assigned_nurse_transition(
            actor=actor,
            request_id=request_id,
            allowed_statuses={CareRequestStatus.ARRIVED},
            next_status=CareRequestStatus.IN_PROGRESS,
            timestamp_field="visit_started_at",
            action="CARE_REQUEST_VISIT_STARTED",
            ip_address=ip_address,
        )

    @transaction.atomic
    def complete(
        self,
        *,
        actor: object,
        request_id: int,
        ip_address: str | None,
    ) -> CareRequest:
        """Complete an in-progress care request."""
        request = self._assigned_nurse_transition(
            actor=actor,
            request_id=request_id,
            allowed_statuses={CareRequestStatus.IN_PROGRESS},
            next_status=CareRequestStatus.COMPLETED,
            timestamp_field="completed_at",
            action="CARE_REQUEST_COMPLETED",
            ip_address=ip_address,
        )
        self._release_assigned_nurse(request)
        return request

    @transaction.atomic
    def cancel(
        self,
        *,
        actor: object,
        request_id: int,
        reason: str,
        ip_address: str | None,
    ) -> CareRequest:
        """Cancel a non-terminal request when actor is patient, assigned nurse, or admin."""
        request = self.selector.get_for_update(request_id=request_id)
        self._ensure_can_cancel(actor=actor, request=request)
        if request.status in TERMINAL_STATUSES:
            raise ValueError("Terminal care requests cannot be cancelled.")

        request.status = CareRequestStatus.CANCELLED
        request.cancelled_at = timezone.now()
        request.cancellation_reason = reason
        request.save(update_fields=["status", "cancelled_at", "cancellation_reason", "updated_at"])
        self._release_assigned_nurse(request)
        self._audit(
            actor=actor,
            action="CARE_REQUEST_CANCELLED",
            request=request,
            ip_address=ip_address,
            metadata={"reason": reason},
        )
        return request

    def _assigned_nurse_transition(
        self,
        *,
        actor: object,
        request_id: int,
        allowed_statuses: set[str],
        next_status: str,
        timestamp_field: str,
        action: str,
        ip_address: str | None,
    ) -> CareRequest:
        """Apply an assigned-nurse-only transition to a locked request row."""
        request = self.selector.get_for_update(request_id=request_id)
        self._ensure_assigned_nurse(actor=actor, request=request)
        if request.status not in allowed_statuses:
            raise ValueError(f"Cannot transition care request from {request.status}.")

        setattr(request, timestamp_field, timezone.now())
        request.status = next_status
        request.save(update_fields=["status", timestamp_field, "updated_at"])
        self._audit(actor=actor, action=action, request=request, ip_address=ip_address)
        return request

    def _dependent_for_patient(
        self,
        *,
        patient: PatientProfile,
        dependent_id: int | None,
    ) -> PatientDependent | None:
        """Return a dependent if it belongs to the patient."""
        if dependent_id is None:
            return None
        try:
            return patient.dependents.get(id=dependent_id)
        except PatientDependent.DoesNotExist as error:
            raise ValueError("Dependent does not belong to this patient.") from error

    def _locked_nurse(self, actor: object) -> NurseProfile:
        """Return the authenticated nurse profile with a row lock."""
        if getattr(actor, "role", None) != UserRole.NURSE:
            raise PermissionError("Only nurses can accept care requests.")
        return NurseProfile.objects.select_for_update().get(user=actor)

    def _ensure_nurse_can_accept(self, nurse: NurseProfile) -> None:
        """Validate nurse eligibility before request acceptance."""
        user = nurse.user
        if not user.email_verified or not user.phone_verified:
            raise ValueError("Email and phone verification are required before accepting requests.")
        if nurse.nck_verification_status != NurseVerificationStatus.VERIFIED:
            raise ValueError("NCK verification is required before accepting requests.")
        if not nurse.is_available or nurse.status != NurseStatus.ONLINE:
            raise ValueError("Nurse must be online and available to accept requests.")

    def _ensure_assigned_nurse(self, *, actor: object, request: CareRequest) -> None:
        """Ensure the actor is the nurse assigned to the request."""
        if getattr(actor, "role", None) != UserRole.NURSE:
            raise PermissionError("Only assigned nurses can perform this action.")
        if not request.assigned_nurse_id or request.assigned_nurse.user_id != actor.id:
            raise PermissionError("Only the assigned nurse can perform this action.")

    def _ensure_can_cancel(self, *, actor: object, request: CareRequest) -> None:
        """Authorize cancellation by patient owner, assigned nurse, or staff admin."""
        role = getattr(actor, "role", None)
        if role == UserRole.PATIENT and request.patient.user_id == actor.id:
            return
        if (
            role == UserRole.NURSE
            and request.assigned_nurse_id
            and request.assigned_nurse.user_id == actor.id
        ):
            return
        if role == UserRole.ADMIN and getattr(actor, "is_staff", False):
            return
        raise PermissionError("You do not have permission to cancel this care request.")

    def _release_assigned_nurse(self, request: CareRequest) -> None:
        """Return the assigned nurse to online status after terminal outcomes."""
        nurse = request.assigned_nurse
        if nurse is None:
            return
        nurse.status = NurseStatus.ONLINE
        nurse.save(update_fields=["status", "updated_at"])

    def _audit(
        self,
        *,
        actor: object,
        action: str,
        request: CareRequest,
        ip_address: str | None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Record a care request audit event."""
        self.audit_service.record(
            actor=actor,
            action=action,
            resource="CareRequest",
            resource_id=request.id,
            ip_address=ip_address,
            metadata={"status": request.status, **(metadata or {})},
        )
