"""Visit management tests."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.db import connection
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import UserRole
from apps.accounts.services.tokens import TokenService
from apps.audit_logs.models import AuditLog, MedicalAccessLog
from apps.nurses.models import NurseProfile, NurseStatus, NurseVerificationStatus
from apps.patients.models import PatientProfile
from apps.requests.models import CareRequest, CareRequestPriority, CareRequestStatus
from apps.visits.models import FollowUpSchedule, VisitNote

User = get_user_model()


@pytest.fixture
def api_client() -> APIClient:
    """Return a DRF API client."""
    return APIClient()


def authenticate(client: APIClient, user: object) -> None:
    """Authenticate a client with a JWT access token."""
    tokens = TokenService().issue_pair(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens.access}")


def create_patient(*, email: str = "visit-patient@example.com") -> object:
    """Create a verified patient user and profile."""
    user = User.objects.create_user(
        email=email,
        password="StrongPassword123!",
        first_name="Visit",
        last_name="Patient",
        role=UserRole.PATIENT,
        email_verified=True,
        phone_verified=True,
    )
    PatientProfile.objects.create(
        user=user,
        phone_number="+254711300000",
        current_location=Point(36.817223, -1.286389, srid=4326),
        last_location_update=timezone.now(),
    )
    return user


def create_nurse(*, email: str = "visit-nurse@example.com") -> object:
    """Create a verified nurse user and profile."""
    user = User.objects.create_user(
        email=email,
        password="StrongPassword123!",
        first_name="Visit",
        last_name="Nurse",
        role=UserRole.NURSE,
        email_verified=True,
        phone_verified=True,
    )
    NurseProfile.objects.create(
        user=user,
        phone_number="+254722300000",
        nck_verification_status=NurseVerificationStatus.VERIFIED,
        nck_license_number=f"NCK-{email}",
        nck_license_expiry="2030-01-01",
        status=NurseStatus.BUSY,
        is_available=True,
        location_visible=True,
        current_location=Point(36.817223, -1.286389, srid=4326),
        last_location_update=timezone.now(),
        rating=Decimal("4.75"),
        reputation_score=Decimal("85.00"),
    )
    return user


def create_admin() -> object:
    """Create an authorized staff administrator."""
    return User.objects.create_user(
        email="visit-admin@example.com",
        password="StrongPassword123!",
        first_name="Visit",
        last_name="Admin",
        role=UserRole.ADMIN,
        is_staff=True,
        email_verified=True,
        phone_verified=True,
    )


def create_in_progress_request(patient_user: object, nurse_user: object) -> CareRequest:
    """Create a care request already in visit state."""
    return CareRequest.objects.create(
        patient=patient_user.patient_profile,
        service_type="GENERAL_NURSING",
        priority=CareRequestPriority.NORMAL,
        description="Visit management setup",
        location=patient_user.patient_profile.current_location,
        requested_time=timezone.now(),
        status=CareRequestStatus.IN_PROGRESS,
        assigned_nurse=nurse_user.nurse_profile,
        accepted_at=timezone.now() - timedelta(minutes=45),
        journey_started_at=timezone.now() - timedelta(minutes=30),
        arrived_at=timezone.now() - timedelta(minutes=10),
        visit_started_at=timezone.now(),
    )


@pytest.mark.django_db
def test_assigned_nurse_creates_encrypted_visit_note_with_follow_up(
    api_client: APIClient,
) -> None:
    """Assigned nurses can create audited encrypted notes for in-progress visits."""
    patient_user = create_patient()
    nurse_user = create_nurse()
    care_request = create_in_progress_request(patient_user, nurse_user)
    authenticate(api_client, nurse_user)

    before_request = timezone.now()
    response = api_client.post(
        reverse("visit-note-list"),
        {
            "care_request_id": care_request.id,
            "vitals": "BP 120/80",
            "observations": "Patient stable",
            "medication_given": "Paracetamol 500mg",
            "recommendations": "Rest and hydrate",
            "follow_up_required": True,
            "follow_up_schedule": FollowUpSchedule.THREE_DAYS,
        },
        format="json",
    )

    note = VisitNote.objects.get()
    assert response.status_code == 201
    assert response.data["vitals"] == "BP 120/80"
    assert response.data["follow_up_schedule"] == FollowUpSchedule.THREE_DAYS
    assert note.follow_up_due_at is not None
    assert note.follow_up_due_at >= before_request + timedelta(days=3)
    assert AuditLog.objects.filter(action="VISIT_NOTE_CREATED", resource_id=str(note.id)).exists()

    with connection.cursor() as cursor:
        cursor.execute("SELECT vitals FROM visits_visitnote WHERE id = %s", [note.id])
        stored_vitals = cursor.fetchone()[0]
    assert stored_vitals.startswith("enc$")


@pytest.mark.django_db
def test_visit_note_creation_requires_assigned_nurse_and_in_progress_request(
    api_client: APIClient,
) -> None:
    """Unassigned nurses and invalid request states cannot create visit notes."""
    patient_user = create_patient()
    nurse_user = create_nurse()
    other_nurse = create_nurse(email="other-visit-nurse@example.com")
    care_request = create_in_progress_request(patient_user, nurse_user)
    authenticate(api_client, other_nurse)

    forbidden_response = api_client.post(
        reverse("visit-note-list"),
        {"care_request_id": care_request.id, "vitals": "BP 120/80"},
        format="json",
    )

    care_request.status = CareRequestStatus.ARRIVED
    care_request.save(update_fields=["status", "updated_at"])
    authenticate(api_client, nurse_user)
    invalid_state_response = api_client.post(
        reverse("visit-note-list"),
        {"care_request_id": care_request.id, "vitals": "BP 120/80"},
        format="json",
    )

    assert forbidden_response.status_code == 403
    assert invalid_state_response.status_code == 400
    assert VisitNote.objects.count() == 0


@pytest.mark.django_db
def test_patient_assigned_nurse_and_admin_can_read_visit_note_with_access_logs(
    api_client: APIClient,
) -> None:
    """Only the patient, assigned nurse, and admin can read protected visit notes."""
    patient_user = create_patient()
    nurse_user = create_nurse()
    admin_user = create_admin()
    care_request = create_in_progress_request(patient_user, nurse_user)
    note = VisitNote.objects.create(
        care_request=care_request,
        patient=patient_user.patient_profile,
        nurse=nurse_user.nurse_profile,
        vitals="BP 120/80",
        observations="Stable",
    )

    authenticate(api_client, patient_user)
    patient_response = api_client.get(reverse("visit-note-detail", kwargs={"note_id": note.id}))

    authenticate(api_client, nurse_user)
    nurse_response = api_client.get(reverse("visit-note-list"))

    authenticate(api_client, admin_user)
    admin_response = api_client.get(reverse("visit-note-detail", kwargs={"note_id": note.id}))

    assert patient_response.status_code == 200
    assert patient_response.data["observations"] == "Stable"
    assert nurse_response.status_code == 200
    assert len(nurse_response.data) == 1
    assert admin_response.status_code == 200
    assert (
        MedicalAccessLog.objects.filter(resource="VisitNote", resource_id=str(note.id)).count() == 3
    )


@pytest.mark.django_db
def test_unrelated_users_cannot_see_or_update_visit_note(api_client: APIClient) -> None:
    """Visit notes are hidden from unrelated patients and nurses."""
    patient_user = create_patient()
    other_patient_user = create_patient(email="other-visit-patient@example.com")
    nurse_user = create_nurse()
    other_nurse_user = create_nurse(email="unrelated-visit-nurse@example.com")
    care_request = create_in_progress_request(patient_user, nurse_user)
    note = VisitNote.objects.create(
        care_request=care_request,
        patient=patient_user.patient_profile,
        nurse=nurse_user.nurse_profile,
        vitals="BP 120/80",
    )

    authenticate(api_client, other_patient_user)
    patient_response = api_client.get(reverse("visit-note-detail", kwargs={"note_id": note.id}))

    authenticate(api_client, other_nurse_user)
    nurse_response = api_client.patch(
        reverse("visit-note-detail", kwargs={"note_id": note.id}),
        {"recommendations": "Should not update"},
        format="json",
    )

    assert patient_response.status_code == 404
    assert nurse_response.status_code == 404
    note.refresh_from_db()
    assert note.recommendations == ""


@pytest.mark.django_db
def test_assigned_nurse_updates_follow_up_schedule(api_client: APIClient) -> None:
    """Assigned nurses can update notes and recalculate follow-up scheduling."""
    patient_user = create_patient()
    nurse_user = create_nurse()
    care_request = create_in_progress_request(patient_user, nurse_user)
    note = VisitNote.objects.create(
        care_request=care_request,
        patient=patient_user.patient_profile,
        nurse=nurse_user.nurse_profile,
        vitals="BP 120/80",
    )
    authenticate(api_client, nurse_user)

    response = api_client.patch(
        reverse("visit-note-detail", kwargs={"note_id": note.id}),
        {
            "recommendations": "Return for dressing review",
            "follow_up_required": True,
            "follow_up_schedule": FollowUpSchedule.ONE_WEEK,
        },
        format="json",
    )

    note.refresh_from_db()
    assert response.status_code == 200
    assert response.data["recommendations"] == "Return for dressing review"
    assert response.data["follow_up_schedule"] == FollowUpSchedule.ONE_WEEK
    assert note.follow_up_due_at is not None
    assert AuditLog.objects.filter(action="VISIT_NOTE_UPDATED", resource_id=str(note.id)).exists()
