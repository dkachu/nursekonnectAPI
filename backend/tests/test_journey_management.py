"""Journey management tests."""

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


def create_patient() -> object:
    """Create a patient profile with a request location."""
    user = User.objects.create_user(
        email="journey-patient@example.com",
        password="StrongPassword123!",
        first_name="Journey",
        last_name="Patient",
        role=UserRole.PATIENT,
        email_verified=True,
        phone_verified=True,
    )
    PatientProfile.objects.create(
        user=user,
        phone_number="+254755000000",
        current_location=Point(36.817223, -1.286389, srid=4326),
        last_location_update=timezone.now(),
    )
    return user


def create_nurse(*, longitude: float = 36.817223, latitude: float = -1.286389) -> object:
    """Create an assigned nurse with a fresh GPS location."""
    user = User.objects.create_user(
        email="journey-nurse@example.com",
        password="StrongPassword123!",
        first_name="Journey",
        last_name="Nurse",
        role=UserRole.NURSE,
        email_verified=True,
        phone_verified=True,
    )
    NurseProfile.objects.create(
        user=user,
        phone_number="+254766000000",
        nck_verification_status=NurseVerificationStatus.VERIFIED,
        nck_license_number="NCK-JOURNEY",
        nck_license_expiry="2030-01-01",
        status=NurseStatus.BUSY,
        is_available=True,
        location_visible=True,
        current_location=Point(longitude, latitude, srid=4326),
        last_location_update=timezone.now(),
        rating=Decimal("4.50"),
        reputation_score=Decimal("80.00"),
    )
    return user


def create_assigned_request(
    *,
    patient_user: object,
    nurse_user: object,
    status: str = CareRequestStatus.ACCEPTED,
) -> CareRequest:
    """Create an assigned care request for journey tests."""
    return CareRequest.objects.create(
        patient=patient_user.patient_profile,
        service_type="GENERAL_NURSING",
        priority=CareRequestPriority.NORMAL,
        description="Journey care",
        location=patient_user.patient_profile.current_location,
        requested_time=timezone.now(),
        status=status,
        assigned_nurse=nurse_user.nurse_profile,
        accepted_at=timezone.now(),
        journey_started_at=timezone.now() if status == CareRequestStatus.NURSE_EN_ROUTE else None,
    )


@pytest.mark.django_db
def test_start_journey_requires_fresh_nurse_gps(api_client: APIClient) -> None:
    """Assigned nurse must have a fresh GPS fix before starting a journey."""
    patient_user = create_patient()
    nurse_user = create_nurse()
    nurse_user.nurse_profile.current_location = None
    nurse_user.nurse_profile.save(update_fields=["current_location", "updated_at"])
    care_request = create_assigned_request(patient_user=patient_user, nurse_user=nurse_user)
    authenticate(api_client, nurse_user)

    response = api_client.post(
        reverse("care-request-start-journey", kwargs={"request_id": care_request.id})
    )

    assert response.status_code == 400
    assert "Fresh nurse GPS" in response.data["detail"]


@pytest.mark.django_db
def test_start_journey_moves_request_en_route(api_client: APIClient) -> None:
    """Assigned nurse can start journey with a fresh GPS fix."""
    patient_user = create_patient()
    nurse_user = create_nurse()
    care_request = create_assigned_request(patient_user=patient_user, nurse_user=nurse_user)
    authenticate(api_client, nurse_user)

    response = api_client.post(
        reverse("care-request-start-journey", kwargs={"request_id": care_request.id})
    )

    care_request.refresh_from_db()
    assert response.status_code == 200
    assert care_request.status == CareRequestStatus.NURSE_EN_ROUTE
    assert care_request.journey_started_at is not None


@pytest.mark.django_db
def test_tracking_requires_active_en_route_request(api_client: APIClient) -> None:
    """Nurse tracking points must belong to an active en-route request."""
    nurse_user = create_nurse()
    authenticate(api_client, nurse_user)

    response = api_client.post(
        reverse("tracking-location"),
        {"latitude": -1.286389, "longitude": 36.817223, "source": "GPS"},
        format="json",
    )

    assert response.status_code == 404
    assert TrackingLocation.objects.count() == 0


@pytest.mark.django_db
def test_tracking_records_request_and_enforces_thirty_second_cadence(
    api_client: APIClient,
) -> None:
    """Tracking records attach to the request and reject updates under 30 seconds apart."""
    patient_user = create_patient()
    nurse_user = create_nurse()
    care_request = create_assigned_request(
        patient_user=patient_user,
        nurse_user=nurse_user,
        status=CareRequestStatus.NURSE_EN_ROUTE,
    )
    authenticate(api_client, nurse_user)

    first = api_client.post(
        reverse("tracking-location"),
        {"latitude": -1.286389, "longitude": 36.817223, "source": "GPS"},
        format="json",
    )
    too_soon = api_client.post(
        reverse("tracking-location"),
        {"latitude": -1.286390, "longitude": 36.817224, "source": "GPS"},
        format="json",
    )
    TrackingLocation.objects.update(recorded_at=timezone.now() - timedelta(seconds=31))
    accepted = api_client.post(
        reverse("tracking-location"),
        {"latitude": -1.286391, "longitude": 36.817225, "source": "GPS"},
        format="json",
    )

    assert first.status_code == 201
    assert first.data["care_request_id"] == care_request.id
    assert too_soon.status_code == 400
    assert "30 seconds" in too_soon.data["detail"]
    assert accepted.status_code == 201
    assert TrackingLocation.objects.filter(care_request=care_request).count() == 2


@pytest.mark.django_db
def test_arrival_requires_nurse_within_100_meters(api_client: APIClient) -> None:
    """Assigned nurse cannot mark arrived unless within 100m of patient location."""
    patient_user = create_patient()
    nurse_user = create_nurse(longitude=36.827223)
    care_request = create_assigned_request(
        patient_user=patient_user,
        nurse_user=nurse_user,
        status=CareRequestStatus.NURSE_EN_ROUTE,
    )
    authenticate(api_client, nurse_user)

    far_response = api_client.post(
        reverse("care-request-arrived", kwargs={"request_id": care_request.id})
    )
    nurse_user.nurse_profile.current_location = patient_user.patient_profile.current_location
    nurse_user.nurse_profile.last_location_update = timezone.now()
    nurse_user.nurse_profile.save(
        update_fields=["current_location", "last_location_update", "updated_at"]
    )
    near_response = api_client.post(
        reverse("care-request-arrived", kwargs={"request_id": care_request.id})
    )

    assert far_response.status_code == 400
    assert "100 meters" in far_response.data["detail"]
    assert near_response.status_code == 200
    assert near_response.data["status"] == CareRequestStatus.ARRIVED


@pytest.mark.django_db
def test_visit_start_requires_nurse_within_100_meters(api_client: APIClient) -> None:
    """Assigned nurse cannot start visit unless still within 100m."""
    patient_user = create_patient()
    nurse_user = create_nurse()
    care_request = create_assigned_request(
        patient_user=patient_user,
        nurse_user=nurse_user,
        status=CareRequestStatus.NURSE_EN_ROUTE,
    )
    authenticate(api_client, nurse_user)
    api_client.post(reverse("care-request-arrived", kwargs={"request_id": care_request.id}))

    nurse_user.nurse_profile.current_location = Point(36.827223, -1.286389, srid=4326)
    nurse_user.nurse_profile.last_location_update = timezone.now()
    nurse_user.nurse_profile.save(
        update_fields=["current_location", "last_location_update", "updated_at"]
    )
    far_response = api_client.post(
        reverse("care-request-start-visit", kwargs={"request_id": care_request.id})
    )
    nurse_user.nurse_profile.current_location = patient_user.patient_profile.current_location
    nurse_user.nurse_profile.last_location_update = timezone.now()
    nurse_user.nurse_profile.save(
        update_fields=["current_location", "last_location_update", "updated_at"]
    )
    near_response = api_client.post(
        reverse("care-request-start-visit", kwargs={"request_id": care_request.id})
    )

    assert far_response.status_code == 400
    assert "100 meters" in far_response.data["detail"]
    assert near_response.status_code == 200
    assert near_response.data["status"] == CareRequestStatus.IN_PROGRESS
