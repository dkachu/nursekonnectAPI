"""Visit note service layer."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from django.db import transaction

from apps.accounts.models import UserRole
from apps.audit_logs.services.audit import AuditLogService
from apps.audit_logs.services.medical_access import MedicalAccessLogService
from apps.requests.models import CareRequest, CareRequestStatus
from apps.visits.models import VisitNote
from apps.visits.selectors import VisitNoteSelector


class VisitNoteService:
    """Create, update, and read visit notes with privacy logging."""

    def __init__(
        self,
        *,
        audit_service: AuditLogService | None = None,
        medical_access_service: MedicalAccessLogService | None = None,
        selector: VisitNoteSelector | None = None,
    ) -> None:
        self.audit_service = audit_service or AuditLogService()
        self.medical_access_service = medical_access_service or MedicalAccessLogService()
        self.selector = selector or VisitNoteSelector()

    @transaction.atomic
    def create(
        self,
        *,
        actor: object,
        data: dict[str, Any],
        ip_address: str | None,
    ) -> VisitNote:
        """Create protected visit notes for an in-progress assigned care request."""
        care_request = self._locked_care_request(care_request_id=int(data.pop("care_request_id")))
        self._ensure_assigned_nurse(actor=actor, care_request=care_request)
        if care_request.status != CareRequestStatus.IN_PROGRESS:
            raise ValueError("Visit notes can only be created during an in-progress visit.")
        if VisitNote.objects.filter(care_request=care_request, is_deleted=False).exists():
            raise ValueError("Visit notes already exist for this care request.")

        note = VisitNote.objects.create(
            care_request=care_request,
            patient=care_request.patient,
            nurse=care_request.assigned_nurse,
            follow_up_due_at=self._follow_up_due_at(data),
            **data,
        )
        self._audit(
            actor=actor,
            action="VISIT_NOTE_CREATED",
            note=note,
            ip_address=ip_address,
        )
        return note

    @transaction.atomic
    def update(
        self,
        *,
        actor: object,
        note: VisitNote,
        data: dict[str, Any],
        ip_address: str | None,
    ) -> VisitNote:
        """Update visit notes as the assigned nurse while the visit is active."""
        self._ensure_assigned_nurse(actor=actor, care_request=note.care_request)
        if note.care_request.status not in {
            CareRequestStatus.IN_PROGRESS,
            CareRequestStatus.COMPLETED,
        }:
            raise ValueError("Visit notes can only be updated for active or completed visits.")

        for field, value in data.items():
            setattr(note, field, value)
        if "follow_up_required" in data or "follow_up_schedule" in data:
            note.follow_up_due_at = self._follow_up_due_at(
                {
                    "follow_up_required": note.follow_up_required,
                    "follow_up_schedule": note.follow_up_schedule,
                }
            )
        note.save()
        self._audit(
            actor=actor,
            action="VISIT_NOTE_UPDATED",
            note=note,
            ip_address=ip_address,
        )
        return note

    def read(
        self,
        *,
        actor: object,
        note: VisitNote,
        ip_address: str | None,
    ) -> VisitNote:
        """Authorize and log a protected visit-note read."""
        self._ensure_can_read(actor=actor, note=note)
        self.medical_access_service.record(
            actor=actor,
            patient=note.patient,
            resource="VisitNote",
            resource_id=note.id,
            action="READ",
            ip_address=ip_address,
        )
        return note

    def log_list_read(
        self,
        *,
        actor: object,
        notes: list[VisitNote],
        ip_address: str | None,
    ) -> None:
        """Log protected visit-note list reads."""
        for note in notes:
            self.read(actor=actor, note=note, ip_address=ip_address)

    def _locked_care_request(self, *, care_request_id: int) -> CareRequest:
        """Return the care request locked for visit-note creation."""
        return (
            CareRequest.objects.select_for_update(of=("self",))
            .select_related("patient", "assigned_nurse", "assigned_nurse__user")
            .get(id=care_request_id, is_deleted=False)
        )

    def _ensure_assigned_nurse(self, *, actor: object, care_request: CareRequest) -> None:
        """Require the actor to be the nurse assigned to the care request."""
        if getattr(actor, "role", None) != UserRole.NURSE:
            raise PermissionError("Only the assigned nurse can manage visit notes.")
        if (
            care_request.assigned_nurse_id is None
            or care_request.assigned_nurse.user_id != actor.id
        ):
            raise PermissionError("Only the assigned nurse can manage visit notes.")

    def _ensure_can_read(self, *, actor: object, note: VisitNote) -> None:
        """Authorize visit-note reads for patient, assigned nurse, or staff admin."""
        role = getattr(actor, "role", None)
        if role == UserRole.PATIENT and note.patient.user_id == actor.id:
            return
        if role == UserRole.NURSE and note.nurse.user_id == actor.id:
            return
        if role == UserRole.ADMIN and getattr(actor, "is_staff", False):
            return
        raise PermissionError("You do not have permission to access this visit note.")

    def _follow_up_due_at(self, data: dict[str, Any]) -> datetime | None:
        """Return a follow-up due timestamp from validated note data."""
        if not data.get("follow_up_required"):
            return None
        return VisitNote.due_at_for_schedule(str(data.get("follow_up_schedule", "")))

    def _audit(
        self,
        *,
        actor: object,
        action: str,
        note: VisitNote,
        ip_address: str | None,
    ) -> None:
        """Record a visit-note audit event."""
        self.audit_service.record(
            actor=actor,
            action=action,
            resource="VisitNote",
            resource_id=note.id,
            ip_address=ip_address,
            metadata={
                "care_request_id": note.care_request_id,
                "patient_id": note.patient_id,
                "nurse_id": note.nurse_id,
            },
        )
