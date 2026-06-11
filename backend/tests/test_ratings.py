"""Rating domain tests."""

from __future__ import annotations

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
from apps.patients.models import PatientProfile
from apps.ratings.models import Rating
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


def create_patient(*, email: str = "rating-patient@example.com") -> object:
    """Create a verified patient and profile."""
    user = User.objects.create_user(
        email=email,
        password="StrongPassword123!",
        first_name="Rating",
        last_name="Patient",
        role=UserRole.PATIENT,
        email_verified=True,
        phone_verified=True,
    )
    PatientProfile.objects.create(
        user=user,
        phone_number="+254711800000",
        current_location=Point(36.817223, -1.286389, srid=4326),
        last_location_update=timezone.now(),
    )
    return user


def create_nurse(*, email: str = "rating-nurse@example.com") -> object:
    """Create a verified nurse and profile."""
    user = User.objects.create_user(
        email=email,
        password="StrongPassword123!",
        first_name="Rating",
        last_name="Nurse",
        role=UserRole.NURSE,
        email_verified=True,
        phone_verified=True,
    )
    NurseProfile.objects.create(
        user=user,
        phone_number="+254722800000",
        nck_verification_status=NurseVerificationStatus.VERIFIED,
        nck_license_number=f"NCK-{email}",
        nck_license_expiry="2030-01-01",
        status=NurseStatus.ONLINE,
        is_available=True,
        location_visible=True,
        current_location=Point(36.827223, -1.286389, srid=4326),
        last_location_update=timezone.now(),
        completed_visits_count=1,
        average_response_seconds=60,
        rating=Decimal("0.00"),
        reputation_score=Decimal("0.00"),
    )
    return user


def create_completed_request(patient_user: object, nurse_user: object) -> CareRequest:
    """Create a completed assigned care request."""
    return CareRequest.objects.create(
        patient=patient_user.patient_profile,
        service_type="GENERAL_NURSING",
        priority=CareRequestPriority.NORMAL,
        description="Completed request",
        location=patient_user.patient_profile.current_location,
        requested_time=timezone.now(),
        status=CareRequestStatus.COMPLETED,
        assigned_nurse=nurse_user.nurse_profile,
        completed_at=timezone.now(),
    )


@pytest.mark.django_db
def test_patient_can_rate_completed_request(api_client: APIClient) -> None:
    """Patients can rate their own completed requests once."""
    patient_user = create_patient()
    nurse_user = create_nurse()
    care_request = create_completed_request(patient_user, nurse_user)
    authenticate(api_client, patient_user)

    response = api_client.post(
        reverse("rating-list"),
        {"care_request_id": care_request.id, "rating": 5, "comment": "Excellent"},
        format="json",
    )

    nurse_user.nurse_profile.refresh_from_db()
    assert response.status_code == 201
    assert response.data["rating"] == 5
    assert Rating.objects.count() == 1
    assert nurse_user.nurse_profile.rating == Decimal("5.00")
    assert nurse_user.nurse_profile.reputation_score > 0
    assert AuditLog.objects.filter(action="RATING_CREATED").exists()


@pytest.mark.django_db
def test_rating_requires_owner_completed_request_and_single_submission(
    api_client: APIClient,
) -> None:
    """Ratings enforce object ownership, completion state, and duplicate protection."""
    patient_user = create_patient()
    other_patient_user = create_patient(email="other-rating-patient@example.com")
    nurse_user = create_nurse()
    care_request = create_completed_request(patient_user, nurse_user)

    authenticate(api_client, other_patient_user)
    forbidden = api_client.post(
        reverse("rating-list"),
        {"care_request_id": care_request.id, "rating": 4},
        format="json",
    )

    authenticate(api_client, patient_user)
    first = api_client.post(
        reverse("rating-list"),
        {"care_request_id": care_request.id, "rating": 4},
        format="json",
    )
    duplicate = api_client.post(
        reverse("rating-list"),
        {"care_request_id": care_request.id, "rating": 5},
        format="json",
    )

    care_request.status = CareRequestStatus.IN_PROGRESS
    care_request.save(update_fields=["status", "updated_at"])
    in_progress = create_completed_request(
        patient_user=create_patient(email="rating-in-progress@example.com"),
        nurse_user=nurse_user,
    )
    in_progress.status = CareRequestStatus.IN_PROGRESS
    in_progress.save(update_fields=["status", "updated_at"])
    invalid_state = api_client.post(
        reverse("rating-list"),
        {"care_request_id": in_progress.id, "rating": 5},
        format="json",
    )

    assert forbidden.status_code == 403
    assert first.status_code == 201
    assert duplicate.status_code == 400
    assert invalid_state.status_code == 403


@pytest.mark.django_db
def test_ratings_list_is_role_scoped(api_client: APIClient) -> None:
    """Patients and nurses only see ratings within their object boundary."""
    patient_user = create_patient()
    nurse_user = create_nurse()
    other_nurse_user = create_nurse(email="other-rating-nurse@example.com")
    care_request = create_completed_request(patient_user, nurse_user)
    Rating.objects.create(
        patient=patient_user.patient_profile,
        nurse=nurse_user.nurse_profile,
        care_request=care_request,
        rating=5,
        comment="Great",
    )

    authenticate(api_client, patient_user)
    patient_response = api_client.get(reverse("rating-list"))
    authenticate(api_client, nurse_user)
    nurse_response = api_client.get(reverse("rating-list"))
    authenticate(api_client, other_nurse_user)
    other_nurse_response = api_client.get(reverse("rating-list"))

    assert patient_response.status_code == 200
    assert len(patient_response.data) == 1
    assert nurse_response.status_code == 200
    assert len(nurse_response.data) == 1
    assert other_nurse_response.status_code == 200
    assert other_nurse_response.data == []
