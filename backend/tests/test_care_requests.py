"""Care request lifecycle tests."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import UserRole
from apps.accounts.services.tokens import TokenService
from apps.audit_logs.models import AuditLog
from apps.nurses.models import NurseProfile, NurseStatus, NurseVerificationStatus
from apps.patients.models import PatientDependent, PatientProfile
from apps.patients.services.access import PatientMedicalAccessService
from apps.requests.models import CareRequest, CareRequestPriority, CareRequestStatus

User = get_user_model()


@pytest.fixture
def api_client() -> APIClient:
    """Return a DRF API client."""
    return APIClient()


def authenticate(client: APIClient, user: object) -> None:
    """Authenticate a client with a JWT access token."""
    tokens = TokenService().issue_pair(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens.access}")


def create_patient(
    *,
    email: str = "request-patient@example.com",
    verified: bool = True,
    fresh_location: bool = True,
) -> object:
    """Create a patient user and profile."""
    user = User.objects.create_user(
        email=email,
        password="StrongPassword123!",
        first_name="Care",
        last_name="Patient",
        role=UserRole.PATIENT,
        email_verified=verified,
        phone_verified=verified,
    )
    PatientProfile.objects.create(
        user=user,
        phone_number="+254711100000",
        current_location=Point(36.817223, -1.286389, srid=4326),
        last_location_update=(
            timezone.now() if fresh_location else timezone.now() - timedelta(minutes=16)
        ),
    )
    return user


def create_nurse(
    *,
    email: str = "request-nurse@example.com",
    status: str = NurseStatus.ONLINE,
    is_available: bool = True,
    verification_status: str = NurseVerificationStatus.VERIFIED,
) -> object:
    """Create a nurse user and profile."""
    user = User.objects.create_user(
        email=email,
        password="StrongPassword123!",
        first_name="Care",
        last_name="Nurse",
        role=UserRole.NURSE,
        email_verified=True,
        phone_verified=True,
    )
    NurseProfile.objects.create(
        user=user,
        phone_number="+254722200000",
        nck_verification_status=verification_status,
        nck_license_number=f"NCK-{email}",
        nck_license_expiry="2030-01-01",
        status=status,
        is_available=is_available,
        location_visible=True,
        current_location=Point(36.827223, -1.286389, srid=4326),
        last_location_update=timezone.now(),
        rating=Decimal("4.50"),
        reputation_score=Decimal("80.00"),
    )
    return user


def create_request_for_patient(patient_user: object) -> CareRequest:
    """Create a pending care request directly for setup."""
    return CareRequest.objects.create(
        patient=patient_user.patient_profile,
        service_type="GENERAL_NURSING",
        priority=CareRequestPriority.NORMAL,
        description="Routine care",
        location=patient_user.patient_profile.current_location,
        requested_time=timezone.now(),
    )


@pytest.mark.django_db
def test_patient_can_create_care_request_from_fresh_gps_location(api_client: APIClient) -> None:
    """Verified patients can create audited pending care requests."""
    patient_user = create_patient()
    dependent = PatientDependent.objects.create(
        patient=patient_user.patient_profile,
        full_name="Care Child",
        date_of_birth="2020-01-01",
        gender="FEMALE",
        relationship="Child",
    )
    authenticate(api_client, patient_user)

    response = api_client.post(
        reverse("care-request-list"),
        {
            "dependent_id": dependent.id,
            "service_type": "WOUND_CARE",
            "priority": "URGENT",
            "description": "Dressing change",
        },
        format="json",
    )

    care_request = CareRequest.objects.get()
    assert response.status_code == 201
    assert response.data["status"] == CareRequestStatus.PENDING
    assert response.data["dependent_id"] == dependent.id
    assert care_request.location.x == pytest.approx(36.817223)
    assert AuditLog.objects.filter(
        action="CARE_REQUEST_CREATED",
        resource_id=str(care_request.id),
    ).exists()


@pytest.mark.django_db
def test_create_request_requires_verified_account_and_fresh_location(api_client: APIClient) -> None:
    """Patients must be verified and have fresh GPS before requesting care."""
    unverified_user = create_patient(email="unverified-request@example.com", verified=False)
    authenticate(api_client, unverified_user)

    response = api_client.post(
        reverse("care-request-list"),
        {"service_type": "WOUND_CARE", "priority": "NORMAL"},
        format="json",
    )

    assert response.status_code == 400
    assert "verification" in response.data["detail"]

    stale_user = create_patient(email="stale-request@example.com", fresh_location=False)
    authenticate(api_client, stale_user)

    response = api_client.post(
        reverse("care-request-list"),
        {"service_type": "WOUND_CARE", "priority": "NORMAL"},
        format="json",
    )

    assert response.status_code == 400
    assert "Fresh patient GPS" in response.data["detail"]


@pytest.mark.django_db
def test_nurse_acceptance_is_single_owner_and_audited(api_client: APIClient) -> None:
    """Only one eligible nurse can accept a pending request."""
    patient_user = create_patient()
    first_nurse = create_nurse(email="first-accept@example.com")
    second_nurse = create_nurse(email="second-accept@example.com")
    care_request = create_request_for_patient(patient_user)

    authenticate(api_client, first_nurse)
    first_response = api_client.post(
        reverse("care-request-accept", kwargs={"request_id": care_request.id}),
        format="json",
    )

    authenticate(api_client, second_nurse)
    second_response = api_client.post(
        reverse("care-request-accept", kwargs={"request_id": care_request.id}),
        format="json",
    )

    care_request.refresh_from_db()
    first_nurse.nurse_profile.refresh_from_db()
    assert first_response.status_code == 200
    assert first_response.data["status"] == CareRequestStatus.ACCEPTED
    assert second_response.status_code == 400
    assert care_request.assigned_nurse == first_nurse.nurse_profile
    assert first_nurse.nurse_profile.status == NurseStatus.BUSY
    assert AuditLog.objects.filter(action="CARE_REQUEST_ACCEPTED").count() == 1


@pytest.mark.django_db
def test_ineligible_nurse_cannot_accept_request(api_client: APIClient) -> None:
    """Nurses must be online, available, and verified to accept requests."""
    patient_user = create_patient()
    nurse_user = create_nurse(
        email="pending-nck@example.com",
        verification_status=NurseVerificationStatus.PENDING,
    )
    care_request = create_request_for_patient(patient_user)
    authenticate(api_client, nurse_user)

    response = api_client.post(
        reverse("care-request-accept", kwargs={"request_id": care_request.id}),
        format="json",
    )

    assert response.status_code == 400
    assert "NCK verification" in response.data["detail"]
    care_request.refresh_from_db()
    assert care_request.assigned_nurse is None


@pytest.mark.django_db
def test_assigned_nurse_transitions_request_to_completed(api_client: APIClient) -> None:
    """Assigned nurse can move through the ordered request lifecycle."""
    patient_user = create_patient()
    nurse_user = create_nurse()
    care_request = create_request_for_patient(patient_user)
    authenticate(api_client, nurse_user)
    api_client.post(reverse("care-request-accept", kwargs={"request_id": care_request.id}))

    for route_name, expected_status in [
        ("care-request-start-journey", CareRequestStatus.NURSE_EN_ROUTE),
        ("care-request-arrived", CareRequestStatus.ARRIVED),
        ("care-request-start-visit", CareRequestStatus.IN_PROGRESS),
        ("care-request-complete", CareRequestStatus.COMPLETED),
    ]:
        response = api_client.post(reverse(route_name, kwargs={"request_id": care_request.id}))
        assert response.status_code == 200
        assert response.data["status"] == expected_status

    care_request.refresh_from_db()
    nurse_user.nurse_profile.refresh_from_db()
    assert care_request.completed_at is not None
    assert nurse_user.nurse_profile.status == NurseStatus.ONLINE
    assert AuditLog.objects.filter(resource_id=str(care_request.id)).count() == 5


@pytest.mark.django_db
def test_invalid_transition_and_unassigned_nurse_are_rejected(api_client: APIClient) -> None:
    """Transition ordering and assigned-nurse ownership are enforced."""
    patient_user = create_patient()
    assigned_nurse = create_nurse(email="assigned-transition@example.com")
    other_nurse = create_nurse(email="other-transition@example.com")
    care_request = create_request_for_patient(patient_user)
    authenticate(api_client, assigned_nurse)
    api_client.post(reverse("care-request-accept", kwargs={"request_id": care_request.id}))

    invalid_response = api_client.post(
        reverse("care-request-start-visit", kwargs={"request_id": care_request.id})
    )

    authenticate(api_client, other_nurse)
    forbidden_response = api_client.post(
        reverse("care-request-start-journey", kwargs={"request_id": care_request.id})
    )

    assert invalid_response.status_code == 400
    assert forbidden_response.status_code == 403


@pytest.mark.django_db
def test_list_and_detail_respect_actor_visibility(api_client: APIClient) -> None:
    """Patients see own requests; nurses see pending and assigned requests."""
    patient_user = create_patient()
    other_patient_user = create_patient(email="other-request-patient@example.com")
    nurse_user = create_nurse()
    own_request = create_request_for_patient(patient_user)
    create_request_for_patient(other_patient_user)

    authenticate(api_client, patient_user)
    patient_list = api_client.get(reverse("care-request-list"))

    authenticate(api_client, nurse_user)
    nurse_list = api_client.get(reverse("care-request-list"))
    nurse_detail = api_client.get(
        reverse("care-request-detail", kwargs={"request_id": own_request.id})
    )

    assert patient_list.status_code == 200
    assert len(patient_list.data) == 1
    assert nurse_list.status_code == 200
    assert len(nurse_list.data) == 2
    assert nurse_detail.status_code == 200
    assert nurse_detail.data["patient_first_name"] == "Care"
    assert nurse_detail.data["patient_last_name"] == ""


@pytest.mark.django_db
def test_cancel_request_and_assigned_medical_access(api_client: APIClient) -> None:
    """Cancellation is audited, and assigned nurses can access protected patient data."""
    patient_user = create_patient()
    nurse_user = create_nurse()
    care_request = create_request_for_patient(patient_user)
    authenticate(api_client, nurse_user)
    api_client.post(reverse("care-request-accept", kwargs={"request_id": care_request.id}))

    assert PatientMedicalAccessService().can_access_medical_data(
        actor=nurse_user,
        patient=patient_user.patient_profile,
    )

    response = api_client.post(
        reverse("care-request-cancel", kwargs={"request_id": care_request.id}),
        {"reason": "Patient no longer available"},
        format="json",
    )

    nurse_user.nurse_profile.refresh_from_db()
    assert response.status_code == 200
    assert response.data["status"] == CareRequestStatus.CANCELLED
    assert nurse_user.nurse_profile.status == NurseStatus.ONLINE
    assert AuditLog.objects.filter(action="CARE_REQUEST_CANCELLED").exists()
