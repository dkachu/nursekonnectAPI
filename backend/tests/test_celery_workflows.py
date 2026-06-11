"""Celery workflow tests for care request automation."""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.utils import timezone

from apps.accounts.models import UserRole
from apps.audit_logs.models import AuditLog
from apps.notifications.models import Notification, NotificationType
from apps.nurses.models import NurseProfile, NurseStatus, NurseVerificationStatus
from apps.patients.models import PatientProfile
from apps.requests.models import (
    CareRequest,
    CareRequestPriority,
    CareRequestStatus,
    RequestOffer,
    RequestOfferStatus,
)
from apps.requests.tasks import (
    CareRequestWorkflowScheduler,
    cancel_stalled_assignment_task,
    send_journey_warning_task,
)
from apps.requests.workflows import CareRequestWorkflowService

User = get_user_model()


class NoopMatchingService:
    """Test double for matching pool return."""

    def __init__(self) -> None:
        self.called = False

    def match_and_notify(self, *, care_request: CareRequest) -> object:
        """Record rematching and return a monitoring-shaped object."""
        self.called = True
        return type(
            "MatchingResult",
            (),
            {"notified_count": 0, "final_radius_km": None},
        )()


def create_patient() -> object:
    """Create a patient user and profile."""
    user = User.objects.create_user(
        email="celery-patient@example.com",
        password="StrongPassword123!",
        first_name="Celery",
        last_name="Patient",
        role=UserRole.PATIENT,
        email_verified=True,
        phone_verified=True,
    )
    PatientProfile.objects.create(
        user=user,
        phone_number="+254777000000",
        current_location=Point(36.817223, -1.286389, srid=4326),
        last_location_update=timezone.now(),
    )
    return user


def create_nurse() -> object:
    """Create a busy assigned nurse."""
    user = User.objects.create_user(
        email="celery-nurse@example.com",
        password="StrongPassword123!",
        first_name="Celery",
        last_name="Nurse",
        role=UserRole.NURSE,
        email_verified=True,
        phone_verified=True,
    )
    NurseProfile.objects.create(
        user=user,
        phone_number="+254788000000",
        nck_verification_status=NurseVerificationStatus.VERIFIED,
        nck_license_number="NCK-CELERY",
        nck_license_expiry="2030-01-01",
        status=NurseStatus.BUSY,
        is_available=True,
        location_visible=True,
        current_location=Point(36.817223, -1.286389, srid=4326),
        last_location_update=timezone.now(),
        rating=Decimal("4.50"),
        reputation_score=Decimal("80.00"),
    )
    return user


def create_accepted_request(patient_user: object, nurse_user: object) -> CareRequest:
    """Create an accepted request with an accepted offer."""
    care_request = CareRequest.objects.create(
        patient=patient_user.patient_profile,
        service_type="GENERAL_NURSING",
        priority=CareRequestPriority.NORMAL,
        description="Workflow request",
        location=patient_user.patient_profile.current_location,
        requested_time=timezone.now(),
        status=CareRequestStatus.ACCEPTED,
        assigned_nurse=nurse_user.nurse_profile,
        accepted_at=timezone.now(),
    )
    RequestOffer.objects.create(
        care_request=care_request,
        nurse=nurse_user.nurse_profile,
        status=RequestOfferStatus.ACCEPTED,
        radius_km=10,
        distance_km=Decimal("2.00"),
        estimated_travel_time=6,
        specialization_match=True,
        rank=1,
        expires_at=timezone.now(),
    )
    return care_request


@pytest.mark.django_db
def test_warning_workflow_sends_one_warning_and_audit_log() -> None:
    """30-minute warning creates one nurse notification and is idempotent."""
    patient_user = create_patient()
    nurse_user = create_nurse()
    care_request = create_accepted_request(patient_user, nurse_user)
    service = CareRequestWorkflowService()

    first = service.send_journey_warning(care_request_id=care_request.id)
    second = service.send_journey_warning(care_request_id=care_request.id)

    assert first.status == "sent"
    assert second.status == "skipped"
    assert second.details["reason"] == "warning_already_sent"
    assert (
        Notification.objects.filter(
            recipient=nurse_user,
            notification_type=NotificationType.JOB_WARNING,
            resource_id=str(care_request.id),
        ).count()
        == 1
    )
    assert AuditLog.objects.filter(action="CARE_REQUEST_JOURNEY_WARNING_SENT").exists()


@pytest.mark.django_db
def test_warning_workflow_skips_when_journey_started() -> None:
    """Warning task skips when the nurse already started moving."""
    patient_user = create_patient()
    nurse_user = create_nurse()
    care_request = create_accepted_request(patient_user, nurse_user)
    care_request.status = CareRequestStatus.NURSE_EN_ROUTE
    care_request.journey_started_at = timezone.now()
    care_request.save(update_fields=["status", "journey_started_at", "updated_at"])

    result = CareRequestWorkflowService().send_journey_warning(care_request_id=care_request.id)

    assert result.status == "skipped"
    assert Notification.objects.count() == 0


@pytest.mark.django_db
def test_stalled_assignment_cancels_assignment_notifies_patient_and_requeues() -> None:
    """60-minute workflow unassigns the nurse and returns request to matching pool."""
    patient_user = create_patient()
    nurse_user = create_nurse()
    care_request = create_accepted_request(patient_user, nurse_user)
    matching_service = NoopMatchingService()

    service = CareRequestWorkflowService(matching_service=matching_service)
    result = service.cancel_stalled_assignment(care_request_id=care_request.id)

    care_request.refresh_from_db()
    nurse_user.nurse_profile.refresh_from_db()
    assert result.status == "requeued"
    assert care_request.status == CareRequestStatus.PENDING
    assert care_request.assigned_nurse is None
    assert care_request.accepted_at is None
    assert nurse_user.nurse_profile.status == NurseStatus.ONLINE
    assert nurse_user.nurse_profile.cancelled_visits_count == 1
    assert RequestOffer.objects.get().status == RequestOfferStatus.CANCELLED
    assert Notification.objects.filter(
        recipient=patient_user,
        notification_type=NotificationType.JOB_CANCELLED,
    ).exists()
    assert AuditLog.objects.filter(action="CARE_REQUEST_ASSIGNMENT_AUTO_CANCELLED").exists()
    assert matching_service.called is True


@pytest.mark.django_db
def test_stalled_assignment_task_skips_after_journey_started() -> None:
    """Auto-cancel task does not disturb an active en-route request."""
    patient_user = create_patient()
    nurse_user = create_nurse()
    care_request = create_accepted_request(patient_user, nurse_user)
    care_request.status = CareRequestStatus.NURSE_EN_ROUTE
    care_request.journey_started_at = timezone.now()
    care_request.save(update_fields=["status", "journey_started_at", "updated_at"])

    result = cancel_stalled_assignment_task.apply(args=[care_request.id]).get()

    care_request.refresh_from_db()
    assert result["status"] == "skipped"
    assert care_request.assigned_nurse == nurse_user.nurse_profile
    assert Notification.objects.count() == 0


@pytest.mark.django_db
def test_warning_task_returns_monitoring_payload() -> None:
    """Celery task returns structured monitoring data."""
    patient_user = create_patient()
    nurse_user = create_nurse()
    care_request = create_accepted_request(patient_user, nurse_user)

    result = send_journey_warning_task.apply(args=[care_request.id]).get()

    assert result["action"] == "journey_warning"
    assert result["care_request_id"] == care_request.id
    assert result["status"] == "sent"


def test_scheduler_uses_30_and_60_minute_countdowns(settings: object) -> None:
    """Workflow scheduler submits delayed warning and cancellation tasks."""
    settings.CELERY_TASK_ALWAYS_EAGER = False
    settings.JOURNEY_WARNING_AFTER_MINUTES = 30
    settings.JOURNEY_CANCEL_AFTER_MINUTES = 60

    with (
        patch("apps.requests.tasks.send_journey_warning_task.apply_async") as warning,
        patch("apps.requests.tasks.cancel_stalled_assignment_task.apply_async") as cancellation,
    ):
        result = CareRequestWorkflowScheduler().schedule_after_acceptance(care_request_id=42)

    assert result == {"warning_scheduled": True, "cancellation_scheduled": True}
    warning.assert_called_once_with(args=[42], countdown=30 * 60)
    cancellation.assert_called_once_with(args=[42], countdown=60 * 60)


def test_tasks_define_retry_strategy() -> None:
    """Celery tasks carry retry settings for transient database failures."""
    assert send_journey_warning_task.autoretry_for
    assert cancel_stalled_assignment_task.autoretry_for
    assert send_journey_warning_task.retry_backoff is True
    assert cancel_stalled_assignment_task.retry_backoff is True
