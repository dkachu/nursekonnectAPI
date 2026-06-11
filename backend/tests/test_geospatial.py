"""Geospatial location update tests."""

from __future__ import annotations

from datetime import timedelta

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
from apps.tracking.selectors import LocationSelector, TrackingLocationSelector
from apps.tracking.services.location_updates import (
    GPS_SOURCE,
    LocationFreshnessService,
    LocationUpdateInput,
    LocationUpdateService,
)

User = get_user_model()


@pytest.fixture
def api_client() -> APIClient:
    """Return a DRF API client."""
    return APIClient()


def authenticate(client: APIClient, user: object) -> None:
    """Authenticate a client with a JWT access token."""
    tokens = TokenService().issue_pair(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens.access}")


@pytest.fixture
def patient_user() -> object:
    """Create a patient user and profile."""
    user = User.objects.create_user(
        email="geo-patient@example.com",
        password="StrongPassword123!",
        first_name="Geo",
        last_name="Patient",
        role=UserRole.PATIENT,
    )
    PatientProfile.objects.create(user=user, phone_number="+254700000030")
    return user


@pytest.fixture
def nurse_user() -> object:
    """Create a verified nurse user and profile."""
    user = User.objects.create_user(
        email="geo-nurse@example.com",
        password="StrongPassword123!",
        first_name="Geo",
        last_name="Nurse",
        role=UserRole.NURSE,
        email_verified=True,
        phone_verified=True,
    )
    NurseProfile.objects.create(
        user=user,
        phone_number="+254700000031",
        nck_verification_status=NurseVerificationStatus.VERIFIED,
        nck_license_number="NCK-GEO",
        nck_license_expiry="2030-01-01",
        status=NurseStatus.ONLINE,
        is_available=True,
        location_visible=True,
        travel_radius_km=100,
    )
    return user


@pytest.mark.django_db
def test_patient_location_update_stores_postgis_point(
    api_client: APIClient,
    patient_user: object,
) -> None:
    """Patient GPS update is stored as a geography point with freshness metadata."""
    authenticate(api_client, patient_user)

    response = api_client.post(
        reverse("location-update"),
        {
            "latitude": -1.286389,
            "longitude": 36.817223,
            "source": GPS_SOURCE,
            "accuracy_meters": 12,
        },
        format="json",
    )

    patient_user.patient_profile.refresh_from_db()
    assert response.status_code == 200
    assert response.data["location_stale"] is False
    assert patient_user.patient_profile.current_location.srid == 4326
    assert patient_user.patient_profile.current_location.x == pytest.approx(36.817223)
    assert patient_user.patient_profile.current_location.y == pytest.approx(-1.286389)


@pytest.mark.django_db
def test_nurse_tracking_location_records_history(
    api_client: APIClient,
    nurse_user: object,
    patient_user: object,
) -> None:
    """Nurse tracking endpoint records immutable journey points and latest location."""
    CareRequest.objects.create(
        patient=patient_user.patient_profile,
        service_type="GENERAL_NURSING",
        priority=CareRequestPriority.NORMAL,
        description="Tracking setup",
        location=Point(36.821946, -1.292066, srid=4326),
        requested_time=timezone.now(),
        status=CareRequestStatus.NURSE_EN_ROUTE,
        assigned_nurse=nurse_user.nurse_profile,
        accepted_at=timezone.now(),
        journey_started_at=timezone.now(),
    )
    authenticate(api_client, nurse_user)

    response = api_client.post(
        reverse("tracking-location"),
        {
            "latitude": -1.292066,
            "longitude": 36.821946,
            "source": GPS_SOURCE,
            "accuracy_meters": 9,
        },
        format="json",
    )

    nurse_user.nurse_profile.refresh_from_db()
    assert response.status_code == 201
    assert TrackingLocation.objects.count() == 1
    assert TrackingLocation.objects.get().care_request is not None
    assert response.data["latitude"] == pytest.approx(-1.292066)
    assert nurse_user.nurse_profile.current_location.x == pytest.approx(36.821946)


@pytest.mark.django_db
def test_manual_location_source_is_rejected(
    api_client: APIClient,
    patient_user: object,
) -> None:
    """The API accepts browser/mobile GPS payloads only."""
    authenticate(api_client, patient_user)

    response = api_client.post(
        reverse("location-update"),
        {"latitude": -1.0, "longitude": 36.0, "source": "MANUAL"},
        format="json",
    )

    assert response.status_code == 400
    assert patient_user.patient_profile.current_location is None


@pytest.mark.django_db
def test_invalid_coordinate_ranges_are_rejected(patient_user: object) -> None:
    """The service validates latitude and longitude ranges."""
    with pytest.raises(ValueError, match="Latitude"):
        LocationUpdateService().point_from_input(
            LocationUpdateInput(latitude=100, longitude=36, source=GPS_SOURCE)
        )
    with pytest.raises(ValueError, match="Longitude"):
        LocationUpdateService().point_from_input(
            LocationUpdateInput(latitude=-1, longitude=190, source=GPS_SOURCE)
        )


@pytest.mark.django_db
def test_location_freshness_uses_fifteen_minute_rule(nurse_user: object) -> None:
    """Locations older than 15 minutes are stale."""
    service = LocationFreshnessService()
    nurse = nurse_user.nurse_profile
    nurse.last_location_update = timezone.now() - timedelta(minutes=16)
    nurse.save(update_fields=["last_location_update", "updated_at"])

    assert service.is_stale(None) is True
    assert service.is_stale(nurse.last_location_update) is True
    assert service.is_stale(timezone.now() - timedelta(minutes=14)) is False


@pytest.mark.django_db
def test_fresh_nurse_selector_filters_stale_and_hidden_nurses(nurse_user: object) -> None:
    """Only fresh, visible, online, verified nurses are eligible location candidates."""
    nurse = nurse_user.nurse_profile
    nurse.current_location = Point(36.817223, -1.286389, srid=4326)
    nurse.last_location_update = timezone.now()
    nurse.save(update_fields=["current_location", "last_location_update", "updated_at"])

    hidden_user = User.objects.create_user(
        email="hidden-geo-nurse@example.com",
        password="StrongPassword123!",
        first_name="Hidden",
        last_name="Nurse",
        role=UserRole.NURSE,
    )
    NurseProfile.objects.create(
        user=hidden_user,
        phone_number="+254700000032",
        current_location=Point(36.817223, -1.286389, srid=4326),
        last_location_update=timezone.now(),
        status=NurseStatus.ONLINE,
        is_available=True,
        location_visible=False,
        nck_verification_status=NurseVerificationStatus.VERIFIED,
    )

    candidates = LocationSelector().candidate_nurses_within_radius(
        origin=Point(36.817223, -1.286389, srid=4326),
        radius_km=10,
    )

    assert list(candidates) == [nurse]
    assert hasattr(candidates[0], "distance_m")


@pytest.mark.django_db
def test_tracking_selector_returns_recent_points(nurse_user: object) -> None:
    """Tracking selector returns recent nurse points in reverse time order."""
    nurse = nurse_user.nurse_profile
    old = TrackingLocation.objects.create(
        nurse=nurse,
        location=Point(36.81, -1.28, srid=4326),
        recorded_at=timezone.now() - timedelta(minutes=5),
    )
    newest = TrackingLocation.objects.create(
        nurse=nurse,
        location=Point(36.82, -1.29, srid=4326),
        recorded_at=timezone.now(),
    )

    results = list(TrackingLocationSelector().recent_for_nurse(nurse, limit=2))

    assert results == [newest, old]
