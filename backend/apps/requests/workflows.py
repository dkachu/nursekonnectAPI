"""Care request delayed workflow services."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from django.db import transaction

from apps.audit_logs.services.audit import AuditLogService
from apps.notifications.models import Notification, NotificationType
from apps.notifications.services import NotificationService
from apps.nurses.models import NurseStatus
from apps.requests.matching import MatchingService
from apps.requests.models import CareRequest, CareRequestStatus, RequestOffer, RequestOfferStatus
from apps.requests.selectors import CareRequestSelector

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class WorkflowResult:
    """Structured monitoring result for workflow tasks."""

    action: str
    care_request_id: int
    status: str
    details: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable monitoring payload."""
        return {
            "action": self.action,
            "care_request_id": self.care_request_id,
            "status": self.status,
            "details": self.details,
        }


class CareRequestWorkflowService:
    """Delayed warning and inactivity cancellation workflows."""

    def __init__(
        self,
        *,
        selector: CareRequestSelector | None = None,
        notification_service: NotificationService | None = None,
        audit_service: AuditLogService | None = None,
        matching_service: MatchingService | None = None,
    ) -> None:
        self.selector = selector or CareRequestSelector()
        self.notification_service = notification_service or NotificationService()
        self.audit_service = audit_service or AuditLogService()
        self.matching_service = matching_service or MatchingService()

    def send_journey_warning(self, *, care_request_id: int) -> WorkflowResult:
        """Warn assigned nurse when journey has not started after 30 minutes."""
        try:
            care_request = self.selector.base_queryset().get(id=care_request_id)
        except CareRequest.DoesNotExist:
            return self._result("journey_warning", care_request_id, "missing")

        if not self._needs_journey_action(care_request):
            return self._result(
                "journey_warning",
                care_request_id,
                "skipped",
                reason=f"status={care_request.status}",
            )
        if Notification.objects.filter(
            notification_type=NotificationType.JOB_WARNING,
            resource="CareRequest",
            resource_id=str(care_request.id),
        ).exists():
            return self._result(
                "journey_warning",
                care_request_id,
                "skipped",
                reason="warning_already_sent",
            )

        notification = self.notification_service.notify(
            recipient=care_request.assigned_nurse.user,
            notification_type=NotificationType.JOB_WARNING,
            title="Journey start reminder",
            body="Please start your journey or the request may be reassigned.",
            payload={
                "care_request_id": care_request.id,
                "status": care_request.status,
                "accepted_at": (
                    care_request.accepted_at.isoformat() if care_request.accepted_at else None
                ),
            },
            resource="CareRequest",
            resource_id=care_request.id,
        )
        self.audit_service.record(
            actor=None,
            action="CARE_REQUEST_JOURNEY_WARNING_SENT",
            resource="CareRequest",
            resource_id=care_request.id,
            ip_address=None,
            metadata={"notification_id": notification.id},
        )
        logger.info(
            "care_request_journey_warning_sent",
            extra={"care_request_id": care_request.id, "notification_id": notification.id},
        )
        return self._result(
            "journey_warning",
            care_request_id,
            "sent",
            notification_id=notification.id,
        )

    @transaction.atomic
    def cancel_stalled_assignment(self, *, care_request_id: int) -> WorkflowResult:
        """Unassign stalled nurse, notify patient, and return request to matching pool."""
        try:
            care_request = (
                self.selector.base_queryset()
                .select_for_update(of=("self",))
                .get(id=care_request_id)
            )
        except CareRequest.DoesNotExist:
            return self._result("stalled_assignment", care_request_id, "missing")

        if not self._needs_journey_action(care_request):
            return self._result(
                "stalled_assignment",
                care_request_id,
                "skipped",
                reason=f"status={care_request.status}",
            )

        previous_nurse = care_request.assigned_nurse
        previous_nurse_id = previous_nurse.id
        care_request.assigned_nurse = None
        care_request.status = CareRequestStatus.PENDING
        care_request.accepted_at = None
        care_request.save(update_fields=["assigned_nurse", "status", "accepted_at", "updated_at"])

        previous_nurse.status = NurseStatus.ONLINE
        previous_nurse.cancelled_visits_count += 1
        previous_nurse.save(update_fields=["status", "cancelled_visits_count", "updated_at"])
        RequestOffer.objects.filter(
            care_request=care_request,
            nurse=previous_nurse,
            status=RequestOfferStatus.ACCEPTED,
        ).update(status=RequestOfferStatus.CANCELLED)

        notification = self.notification_service.notify(
            recipient=care_request.patient.user,
            notification_type=NotificationType.JOB_CANCELLED,
            title="Nurse assignment cancelled",
            body="Your nurse assignment was cancelled because the journey did not start.",
            payload={
                "care_request_id": care_request.id,
                "previous_nurse_id": previous_nurse_id,
                "returned_to_matching": True,
            },
            resource="CareRequest",
            resource_id=care_request.id,
        )
        self.audit_service.record(
            actor=None,
            action="CARE_REQUEST_ASSIGNMENT_AUTO_CANCELLED",
            resource="CareRequest",
            resource_id=care_request.id,
            ip_address=None,
            metadata={
                "previous_nurse_id": previous_nurse_id,
                "notification_id": notification.id,
            },
        )
        matching_result = self.matching_service.match_and_notify(care_request=care_request)
        logger.warning(
            "care_request_assignment_auto_cancelled",
            extra={
                "care_request_id": care_request.id,
                "previous_nurse_id": previous_nurse_id,
                "new_offers": matching_result.notified_count,
            },
        )
        return self._result(
            "stalled_assignment",
            care_request_id,
            "requeued",
            previous_nurse_id=previous_nurse_id,
            patient_notification_id=notification.id,
            new_offers=matching_result.notified_count,
            final_radius_km=matching_result.final_radius_km,
        )

    def _needs_journey_action(self, care_request: CareRequest) -> bool:
        """Return whether a request still has no journey after acceptance."""
        return bool(
            care_request.assigned_nurse_id
            and care_request.journey_started_at is None
            and care_request.status in {CareRequestStatus.ACCEPTED, CareRequestStatus.PREPARING}
        )

    def _result(
        self,
        action: str,
        care_request_id: int,
        status: str,
        **details: Any,
    ) -> WorkflowResult:
        """Build and log a structured workflow result."""
        result = WorkflowResult(
            action=action,
            care_request_id=care_request_id,
            status=status,
            details=details,
        )
        logger.info("care_request_workflow_result", extra=result.as_dict())
        return result
