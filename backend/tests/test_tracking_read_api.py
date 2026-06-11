"""Request-scoped journey tracking read API tests."""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import UserRole
from apps.accounts.services.tokens import TokenService
from apps.nurses.models import NurseProfile, NurseStatus, NurseVerificationStatus
from apps.patients.models import PatientProfile
from apps.requests.models import CareRequest, CareRequestPriority, CareRequestStatus
from apps.tracking.models import TrackingLocation

User = get_user_model()


@pytest.fixture
def api_client() -> APIClient:
    """Return a DRF API client."""
    return APIClient()


def authenticate(client: APIClient, user: object) -> None:
    """Authenticate a client with a JWT access token."""
    tokens = TokenService().issue_pair(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens.access}")


def create_patient(email: str) -> object:
    """Create a verified patient with a fresh location."""
    user = User.objects.create_user(
        email=email,
        password="StrongPassword123!",
        first_name="Track",
        last_name="Patient",
        role=UserRole.PATIENT,
        email_verified=True,
        phone_verified=True,
    )
    PatientProfile.objects.create(
        user=user,
        phone_number="+254711600000",
        current_location=Point(36.817223, -1.286389, srid=4326),
        last_location_update=timezone.now(),
    )
    return user


def create_nurse(email: str) -> object:
    """Create a verified nurse with a fresh visible location."""
    user = User.objects.create_user(
        email=email,
        password="StrongPassword123!",
        first_name="Track",
        last_name="Nurse",
        role=UserRole.NURSE,
        email_verified=True,
        phone_verified=True,
    )
    NurseProfile.objects.create(
        user=user,
        phone_number="+254722600000",
        nck_verification_status=NurseVerificationStatus.VERIFIED,
        nck_license_number=f"NCK-{email}",
        nck_license_expiry="2030-01-01",
        status=NurseStatus.ONLINE,
        is_available=True,
        location_visible=True,
        current_location=Point(36.827223, -1.286389, srid=4326),
        last_location_update=timezone.now(),
    )
    return user


@pytest.mark.django_db
def test_patient_can_read_assigned_request_tracking_history(api_client: APIClient) -> None:
    """Patients can read tracking points for their assigned active request."""
    patient = create_patient("tracking-patient@example.com")
    nurse = create_nurse("tracking-nurse@example.com")
    care_request = CareRequest.objects.create(
        patient=patient.patient_profile,
        service_type="GENERAL_NURSING",
        priority=CareRequestPriority.NORMAL,
        description="Track the nurse",
        location=patient.patient_profile.current_location,
        requested_time=timezone.now(),
        status=CareRequestStatus.NURSE_EN_ROUTE,
        assigned_nurse=nurse.nurse_profile,
        accepted_at=timezone.now(),
        journey_started_at=timezone.now(),
    )
    location = TrackingLocation.objects.create(
        nurse=nurse.nurse_profile,
        care_request=care_request,
        location=Point(36.827223, -1.286389, srid=4326),
        recorded_at=timezone.now(),
    )
    authenticate(api_client, patient)

    response = api_client.get(
        reverse("tracking-request-location-list", kwargs={"request_id": care_request.id})
    )

    assert response.status_code == 200
    assert response.data[0]["id"] == location.id
    assert response.data[0]["care_request_id"] == care_request.id


@pytest.mark.django_db
def test_unassigned_nurse_cannot_read_request_tracking_history(api_client: APIClient) -> None:
    """Nurses who do not own a request cannot read journey tracking history."""
    patient = create_patient("tracking-private-patient@example.com")
    assigned_nurse = create_nurse("tracking-private-assigned@example.com")
    other_nurse = create_nurse("tracking-private-other@example.com")
    care_request = CareRequest.objects.create(
        patient=patient.patient_profile,
        service_type="GENERAL_NURSING",
        priority=CareRequestPriority.NORMAL,
        description="Private tracking",
        location=patient.patient_profile.current_location,
        requested_time=timezone.now(),
        status=CareRequestStatus.NURSE_EN_ROUTE,
        assigned_nurse=assigned_nurse.nurse_profile,
        accepted_at=timezone.now(),
        journey_started_at=timezone.now(),
    )
    authenticate(api_client, other_nurse)

    response = api_client.get(
        reverse("tracking-request-location-list", kwargs={"request_id": care_request.id})
    )

    assert response.status_code == 404
