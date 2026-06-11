"""Nearby nurse discovery tests."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from typing import Any
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import UserRole
from apps.accounts.services.tokens import TokenService
from apps.nurses.models import (
    NurseProfile,
    NurseSpecialization,
    NurseStatus,
    NurseVerificationStatus,
)
from apps.nurses.services.discovery import OSRMRouteService
from apps.patients.models import PatientProfile

User = get_user_model()


@pytest.fixture
def api_client() -> APIClient:
    """Return a DRF API client."""
    return APIClient()


def authenticate(client: APIClient, user: object) -> None:
    """Authenticate a client with a JWT access token."""
    tokens = TokenService().issue_pair(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens.access}")


def create_patient(*, email: str = "nearby-patient@example.com") -> object:
    """Create a patient with a fresh Nairobi GPS point."""
    user = User.objects.create_user(
        email=email,
        password="StrongPassword123!",
        first_name="Nearby",
        last_name="Patient",
        role=UserRole.PATIENT,
    )
    PatientProfile.objects.create(
        user=user,
        phone_number="+254711000000",
        current_location=Point(36.817223, -1.286389, srid=4326),
        last_location_update=timezone.now(),
    )
    return user


def create_nurse(
    *,
    email: str,
    longitude: float,
    latitude: float = -1.286389,
    status: str = NurseStatus.ONLINE,
    is_available: bool = True,
    location_visible: bool = True,
    verification_status: str = NurseVerificationStatus.VERIFIED,
    last_location_update: object | None = None,
    reputation_score: Decimal = Decimal("50.00"),
    average_response_seconds: int = 60,
    specialization_code: str | None = None,
) -> NurseProfile:
    """Create a nurse profile with location and ranking fields."""
    user = User.objects.create_user(
        email=email,
        password="StrongPassword123!",
        first_name=email.split("@")[0],
        last_name="Nurse",
        role=UserRole.NURSE,
        email_verified=True,
        phone_verified=True,
    )
    nurse = NurseProfile.objects.create(
        user=user,
        phone_number=f"+2547{User.objects.count():08d}",
        nck_verification_status=verification_status,
        nck_license_number=f"NCK-{User.objects.count()}",
        nck_license_expiry="2030-01-01",
        status=status,
        is_available=is_available,
        location_visible=location_visible,
        current_location=Point(longitude, latitude, srid=4326),
        last_location_update=last_location_update or timezone.now(),
        travel_radius_km=100,
        years_of_experience=5,
        rating=Decimal("4.50"),
        reputation_score=reputation_score,
        average_response_seconds=average_response_seconds,
    )
    if specialization_code:
        nurse.specializations.add(NurseSpecialization.objects.get(code=specialization_code))
    return nurse


def route_result(distance_km: float, minutes: int) -> object:
    """Return a lightweight route estimate for patched OSRM calls."""
    return type(
        "RouteResult",
        (),
        {"distance_km": distance_km, "estimated_travel_time": minutes},
    )()


@pytest.mark.django_db
def test_nearby_nurses_returns_only_eligible_osrm_ranked_results(
    api_client: APIClient,
) -> None:
    """Discovery filters eligibility with PostGIS and returns OSRM distance and ETA."""
    patient_user = create_patient()
    authenticate(api_client, patient_user)
    eligible = create_nurse(email="eligible@example.com", longitude=36.827223)
    create_nurse(email="hidden@example.com", longitude=36.828223, location_visible=False)
    create_nurse(email="offline@example.com", longitude=36.829223, status=NurseStatus.OFFLINE)
    create_nurse(email="busy@example.com", longitude=36.830223, status=NurseStatus.BUSY)
    create_nurse(email="unavailable@example.com", longitude=36.831223, is_available=False)
    create_nurse(
        email="pending@example.com",
        longitude=36.832223,
        verification_status=NurseVerificationStatus.PENDING,
    )
    create_nurse(
        email="stale@example.com",
        longitude=36.833223,
        last_location_update=timezone.now() - timedelta(minutes=16),
    )
    create_nurse(email="road-far@example.com", longitude=36.834223)
    create_nurse(email="postgis-far@example.com", longitude=39.668206, latitude=-4.043477)

    def fake_route(*, origin: Point, destination: Point) -> object:
        if abs(destination.x - eligible.current_location.x) < 0.000001:
            return route_result(12.4, 18)
        return route_result(101.0, 150)

    with patch("apps.nurses.services.discovery.OSRMRouteService.route", side_effect=fake_route):
        response = api_client.get(reverse("nearby-nurses"))

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["id"] == eligible.id
    assert response.data[0]["distance_km"] == pytest.approx(12.4)
    assert response.data[0]["estimated_travel_time"] == 18
    assert "current_location" not in response.data[0]
    assert "phone_number" not in response.data[0]


@pytest.mark.django_db
def test_nearby_nurses_ranking_uses_distance_reputation_response_then_specialization(
    api_client: APIClient,
) -> None:
    """Ranking follows road distance, reputation, response speed, specialization match."""
    patient_user = create_patient(email="ranking-patient@example.com")
    authenticate(api_client, patient_user)
    near = create_nurse(
        email="near-low-reputation@example.com",
        longitude=36.821223,
        reputation_score=Decimal("10.00"),
    )
    high_reputation = create_nurse(
        email="high-reputation@example.com",
        longitude=36.822223,
        reputation_score=Decimal("90.00"),
        average_response_seconds=300,
    )
    faster = create_nurse(
        email="faster@example.com",
        longitude=36.823223,
        reputation_score=Decimal("80.00"),
        average_response_seconds=20,
    )
    specialization_match = create_nurse(
        email="specialization-match@example.com",
        longitude=36.824223,
        reputation_score=Decimal("80.00"),
        average_response_seconds=20,
        specialization_code="WOUND_CARE",
    )
    slower = create_nurse(
        email="slower@example.com",
        longitude=36.825223,
        reputation_score=Decimal("80.00"),
        average_response_seconds=120,
    )
    route_distances = {
        round(near.current_location.x, 6): route_result(5.0, 9),
        round(high_reputation.current_location.x, 6): route_result(8.0, 12),
        round(faster.current_location.x, 6): route_result(8.0, 12),
        round(specialization_match.current_location.x, 6): route_result(8.0, 12),
        round(slower.current_location.x, 6): route_result(8.0, 12),
    }

    def fake_route(*, origin: Point, destination: Point) -> object:
        return route_distances[round(destination.x, 6)]

    with patch("apps.nurses.services.discovery.OSRMRouteService.route", side_effect=fake_route):
        response = api_client.get(
            reverse("nearby-nurses"),
            {"specialization": "WOUND_CARE"},
        )

    assert response.status_code == 200
    assert [item["id"] for item in response.data] == [
        near.id,
        high_reputation.id,
        specialization_match.id,
        faster.id,
        slower.id,
    ]
    assert response.data[2]["specialization_match"] is True
    assert response.data[3]["specialization_match"] is False


@pytest.mark.django_db
def test_nearby_nurses_requires_fresh_patient_location(api_client: APIClient) -> None:
    """Patients must submit a fresh GPS location before discovery."""
    patient_user = create_patient(email="stale-patient@example.com")
    patient_user.patient_profile.last_location_update = timezone.now() - timedelta(minutes=16)
    patient_user.patient_profile.save(update_fields=["last_location_update", "updated_at"])
    authenticate(api_client, patient_user)

    response = api_client.get(reverse("nearby-nurses"))

    assert response.status_code == 400
    assert (
        response.data["detail"]
        == "Fresh patient GPS location is required before discovering nurses."
    )


@pytest.mark.django_db
def test_nearby_nurses_is_patient_only(api_client: APIClient) -> None:
    """Nurses cannot query patient nearby discovery."""
    nurse = create_nurse(email="requesting-nurse@example.com", longitude=36.827223)
    authenticate(api_client, nurse.user)

    response = api_client.get(reverse("nearby-nurses"))

    assert response.status_code == 403


def test_osrm_route_service_parses_distance_eta_and_uses_coordinate_order(
    settings: object,
) -> None:
    """OSRM adapter parses route distance, ETA, and longitude-latitude URL order."""
    settings.OSRM_BASE_URL = "http://osrm.test"
    settings.OSRM_REQUEST_TIMEOUT_SECONDS = 2

    class FakeResponse:
        def __enter__(self) -> FakeResponse:
            return self

        def __exit__(self, *args: Any) -> None:
            return None

        def read(self) -> bytes:
            return b'{"routes": [{"distance": 12400, "duration": 1080}]}'

    captured_urls: list[str] = []

    def fake_urlopen(request: object, timeout: int) -> FakeResponse:
        captured_urls.append(request.full_url)
        assert timeout == 2
        return FakeResponse()

    with patch("apps.nurses.services.discovery.urllib.request.urlopen", side_effect=fake_urlopen):
        result = OSRMRouteService().route(
            origin=Point(36.817223, -1.286389, srid=4326),
            destination=Point(36.827223, -1.296389, srid=4326),
        )

    assert captured_urls == [
        "http://osrm.test/route/v1/driving/"
        "36.817223,-1.286389;36.827223,-1.296389?overview=false"
    ]
    assert result.distance_km == pytest.approx(12.4)
    assert result.estimated_travel_time == 18
