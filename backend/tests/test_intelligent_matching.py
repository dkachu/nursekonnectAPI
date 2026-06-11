"""Intelligent nurse matching tests."""

from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import UserRole
from apps.accounts.services.tokens import TokenService
from apps.notifications.models import Notification, NotificationType
from apps.nurses.models import (
    NurseProfile,
    NurseSpecialization,
    NurseStatus,
    NurseVerificationStatus,
    TravelRadiusKm,
)
from apps.nurses.services.discovery import RouteEstimate
from apps.patients.models import PatientProfile
from apps.requests.matching import MatchingService, NurseMatchCandidate, RankingService
from apps.requests.models import (
    CareRequest,
    CareRequestPriority,
    RequestOffer,
    RequestOfferStatus,
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


def create_patient() -> object:
    """Create a verified patient with a fresh GPS location."""
    user = User.objects.create_user(
        email="matching-patient@example.com",
        password="StrongPassword123!",
        first_name="Match",
        last_name="Patient",
        role=UserRole.PATIENT,
        email_verified=True,
        phone_verified=True,
    )
    PatientProfile.objects.create(
        user=user,
        phone_number="+254733000000",
        current_location=Point(36.817223, -1.286389, srid=4326),
        last_location_update=timezone.now(),
    )
    return user


def create_nurse(
    *,
    email: str,
    longitude: float,
    specialization_code: str,
    travel_radius_km: int = TravelRadiusKm.HUNDRED,
    reputation_score: Decimal = Decimal("50.00"),
    average_response_seconds: int = 60,
) -> NurseProfile:
    """Create an eligible nurse with one specialization."""
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
        phone_number="+254744000000",
        nck_verification_status=NurseVerificationStatus.VERIFIED,
        nck_license_number=f"NCK-{email}",
        nck_license_expiry="2030-01-01",
        status=NurseStatus.ONLINE,
        is_available=True,
        location_visible=True,
        current_location=Point(longitude, -1.286389, srid=4326),
        last_location_update=timezone.now(),
        travel_radius_km=travel_radius_km,
        reputation_score=reputation_score,
        average_response_seconds=average_response_seconds,
    )
    nurse.specializations.add(NurseSpecialization.objects.get(code=specialization_code))
    return nurse


def create_care_request(patient_user: object, service_type: str = "WOUND_CARE") -> CareRequest:
    """Create a pending care request for direct matching tests."""
    return CareRequest.objects.create(
        patient=patient_user.patient_profile,
        service_type=service_type,
        priority=CareRequestPriority.NORMAL,
        description="Matching request",
        location=patient_user.patient_profile.current_location,
        requested_time=timezone.now(),
    )


def route_map_for(nurses: list[NurseProfile], distances: list[float]) -> dict[float, RouteEstimate]:
    """Map nurse longitudes to fake OSRM estimates."""
    return {
        round(nurse.current_location.x, 6): RouteEstimate(
            distance_km=distance, estimated_travel_time=10
        )
        for nurse, distance in zip(nurses, distances, strict=True)
    }


def test_ranking_service_orders_by_distance_specialization_reputation_response() -> None:
    """RankingService uses deterministic matching priority fields."""
    nurse_a = SimpleNamespace(reputation_score=Decimal("20.00"), average_response_seconds=30)
    nurse_b = SimpleNamespace(reputation_score=Decimal("90.00"), average_response_seconds=30)
    nurse_c = SimpleNamespace(reputation_score=Decimal("90.00"), average_response_seconds=10)
    nurse_d = SimpleNamespace(reputation_score=Decimal("90.00"), average_response_seconds=10)
    candidates = [
        NurseMatchCandidate(
            nurse=nurse_b,
            distance_km=8,
            estimated_travel_time=12,
            specialization_match=True,
            radius_km=10,
        ),
        NurseMatchCandidate(
            nurse=nurse_a,
            distance_km=5,
            estimated_travel_time=8,
            specialization_match=True,
            radius_km=10,
        ),
        NurseMatchCandidate(
            nurse=nurse_c,
            distance_km=8,
            estimated_travel_time=12,
            specialization_match=False,
            radius_km=10,
        ),
        NurseMatchCandidate(
            nurse=nurse_d,
            distance_km=8,
            estimated_travel_time=12,
            specialization_match=True,
            radius_km=10,
        ),
    ]

    ranked = RankingService().rank(candidates)

    assert [candidate.nurse for candidate in ranked] == [nurse_a, nurse_d, nurse_b, nurse_c]


@pytest.mark.django_db
def test_matching_notifies_nearest_five_and_never_entire_network(settings: object) -> None:
    """MatchingService notifies a bounded nearest batch only."""
    settings.MATCHING_RADIUS_STEPS_KM = [10, 20, 50, 100]
    patient_user = create_patient()
    nurses = [
        create_nurse(
            email=f"bounded-{index}@example.com",
            longitude=36.817223 + index * 0.001,
            specialization_code="WOUND_CARE",
        )
        for index in range(1, 9)
    ]
    care_request = create_care_request(patient_user)
    routes = route_map_for(nurses, [1, 2, 3, 4, 5, 6, 7, 8])

    def fake_route(*, origin: Point, destination: Point) -> RouteEstimate:
        return routes[round(destination.x, 6)]

    with patch("apps.nurses.services.discovery.OSRMRouteService.route", side_effect=fake_route):
        result = MatchingService().match_and_notify(care_request=care_request)

    assert result.notified_count == 5
    assert RequestOffer.objects.count() == 5
    assert Notification.objects.count() == 5
    assert list(RequestOffer.objects.order_by("rank").values_list("nurse_id", flat=True)) == [
        nurse.id for nurse in nurses[:5]
    ]
    assert not RequestOffer.objects.filter(nurse__in=nurses[5:]).exists()


@pytest.mark.django_db
def test_matching_expands_radius_gradually(settings: object) -> None:
    """MatchingService expands radius only until the batch is filled."""
    settings.MATCHING_RADIUS_STEPS_KM = [10, 20, 50, 100]
    patient_user = create_patient()
    nurses = [
        create_nurse(
            email=f"radius-{index}@example.com",
            longitude=36.817223 + index * 0.001,
            specialization_code="WOUND_CARE",
        )
        for index in range(1, 7)
    ]
    care_request = create_care_request(patient_user)
    routes = route_map_for(nurses, [4, 8, 12, 15, 18, 40])

    def fake_route(*, origin: Point, destination: Point) -> RouteEstimate:
        return routes[round(destination.x, 6)]

    with patch("apps.nurses.services.discovery.OSRMRouteService.route", side_effect=fake_route):
        result = MatchingService().match_and_notify(care_request=care_request)

    assert result.notified_count == 5
    assert result.final_radius_km == 20
    assert set(RequestOffer.objects.values_list("radius_km", flat=True)) == {10, 20}


@pytest.mark.django_db
def test_matching_respects_travel_radius_and_specialization(settings: object) -> None:
    """Nurses outside travel radius or missing specialization are excluded."""
    settings.MATCHING_RADIUS_STEPS_KM = [20, 50, 100]
    patient_user = create_patient()
    too_far_for_nurse = create_nurse(
        email="travel-radius@example.com",
        longitude=36.827223,
        specialization_code="WOUND_CARE",
        travel_radius_km=TravelRadiusKm.TEN,
    )
    wrong_specialization = create_nurse(
        email="wrong-specialization@example.com",
        longitude=36.828223,
        specialization_code="GENERAL_NURSING",
    )
    eligible = create_nurse(
        email="eligible-specialization@example.com",
        longitude=36.829223,
        specialization_code="WOUND_CARE",
        travel_radius_km=TravelRadiusKm.TWENTY,
    )
    care_request = create_care_request(patient_user)
    routes = route_map_for([too_far_for_nurse, wrong_specialization, eligible], [12, 5, 15])

    def fake_route(*, origin: Point, destination: Point) -> RouteEstimate:
        return routes[round(destination.x, 6)]

    with patch("apps.nurses.services.discovery.OSRMRouteService.route", side_effect=fake_route):
        result = MatchingService().match_and_notify(care_request=care_request)

    assert result.notified_count == 1
    assert RequestOffer.objects.get().nurse == eligible
    assert Notification.objects.get().recipient == eligible.user


@pytest.mark.django_db
def test_create_request_integration_generates_offers_and_notifications(
    api_client: APIClient,
    settings: object,
) -> None:
    """Creating a request invokes matching and persists safe nurse notifications."""
    settings.MATCHING_RADIUS_STEPS_KM = [10, 20, 50, 100]
    patient_user = create_patient()
    nurses = [
        create_nurse(
            email=f"integration-{index}@example.com",
            longitude=36.817223 + index * 0.001,
            specialization_code="WOUND_CARE",
        )
        for index in range(1, 7)
    ]
    routes = route_map_for(nurses, [1, 2, 3, 4, 5, 6])
    authenticate(api_client, patient_user)

    def fake_route(*, origin: Point, destination: Point) -> RouteEstimate:
        return routes[round(destination.x, 6)]

    with patch("apps.nurses.services.discovery.OSRMRouteService.route", side_effect=fake_route):
        response = api_client.post(
            reverse("care-request-list"),
            {"service_type": "WOUND_CARE", "priority": "URGENT"},
            format="json",
        )

    assert response.status_code == 201
    assert RequestOffer.objects.count() == 5
    assert Notification.objects.filter(notification_type=NotificationType.JOB_ASSIGNED).count() == 5
    notification = Notification.objects.order_by("created_at").first()
    assert "allergies" not in notification.payload
    assert notification.payload["service_type"] == "WOUND_CARE"


@pytest.mark.django_db
def test_acceptance_requires_active_offer_when_matching_created_offers(
    api_client: APIClient,
    settings: object,
) -> None:
    """Only nurses with active offers can accept a distributed request."""
    settings.MATCHING_RADIUS_STEPS_KM = [10, 20, 50, 100]
    patient_user = create_patient()
    offered_nurse = create_nurse(
        email="offered@example.com", longitude=36.818223, specialization_code="WOUND_CARE"
    )
    unoffered_nurse = create_nurse(
        email="unoffered@example.com",
        longitude=36.819223,
        specialization_code="GENERAL_NURSING",
    )
    care_request = create_care_request(patient_user)
    routes = route_map_for([offered_nurse, unoffered_nurse], [1, 30])

    def fake_route(*, origin: Point, destination: Point) -> RouteEstimate:
        return routes[round(destination.x, 6)]

    with patch("apps.nurses.services.discovery.OSRMRouteService.route", side_effect=fake_route):
        MatchingService().match_and_notify(care_request=care_request)

    authenticate(api_client, unoffered_nurse.user)
    forbidden = api_client.post(
        reverse("care-request-accept", kwargs={"request_id": care_request.id})
    )
    authenticate(api_client, offered_nurse.user)
    accepted = api_client.post(
        reverse("care-request-accept", kwargs={"request_id": care_request.id})
    )

    assert forbidden.status_code == 403
    assert accepted.status_code == 200
    assert RequestOffer.objects.get(nurse=offered_nurse).status == RequestOfferStatus.ACCEPTED


@pytest.mark.django_db
def test_matching_query_count_is_bounded_for_candidate_batch(
    settings: object,
) -> None:
    """Matching keeps DB work bounded while notifying only five nurses."""
    settings.MATCHING_RADIUS_STEPS_KM = [100]
    patient_user = create_patient()
    nurses = [
        create_nurse(
            email=f"perf-{index}@example.com",
            longitude=36.817223 + index * 0.001,
            specialization_code="WOUND_CARE",
        )
        for index in range(1, 13)
    ]
    care_request = create_care_request(patient_user)
    routes = route_map_for(nurses, list(range(1, 13)))

    def fake_route(*, origin: Point, destination: Point) -> RouteEstimate:
        return routes[round(destination.x, 6)]

    with patch("apps.nurses.services.discovery.OSRMRouteService.route", side_effect=fake_route):
        with CaptureQueriesContext(connection) as context:
            MatchingService().match_and_notify(care_request=care_request)

    assert len(context) <= 25
    assert RequestOffer.objects.count() == 5
    assert Notification.objects.count() == 5
