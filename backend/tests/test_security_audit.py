"""Security audit regression tests."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import UserRole
from apps.accounts.services.tokens import TokenService
from apps.nurses.models import NurseProfile, NurseStatus, NurseVerificationStatus
from apps.patients.models import PatientDependent, PatientProfile
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


def create_patient(*, email: str) -> object:
    """Create a verified patient with a profile."""
    user = User.objects.create_user(
        email=email,
        password="StrongPassword123!",
        first_name="Secure",
        last_name="Patient",
        role=UserRole.PATIENT,
        email_verified=True,
        phone_verified=True,
    )
    PatientProfile.objects.create(
        user=user,
        phone_number="+254711500000",
        current_location=Point(36.817223, -1.286389, srid=4326),
        last_location_update=timezone.now(),
    )
    return user


def create_nurse(*, email: str) -> object:
    """Create a verified nurse with a profile."""
    user = User.objects.create_user(
        email=email,
        password="StrongPassword123!",
        first_name="Secure",
        last_name="Nurse",
        role=UserRole.NURSE,
        email_verified=True,
        phone_verified=True,
    )
    NurseProfile.objects.create(
        user=user,
        phone_number="+254722500000",
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


def create_request(patient_user: object) -> CareRequest:
    """Create a pending request with sensitive narrative data."""
    dependent = PatientDependent.objects.create(
        patient=patient_user.patient_profile,
        full_name="Private Child",
        date_of_birth="2020-01-01",
        gender="FEMALE",
        relationship="Child",
        medical_notes="Sensitive dependent detail",
    )
    return CareRequest.objects.create(
        patient=patient_user.patient_profile,
        dependent=dependent,
        service_type="GENERAL_NURSING",
        priority=CareRequestPriority.NORMAL,
        description="Sensitive symptoms and address notes",
        location=patient_user.patient_profile.current_location,
        requested_time=timezone.now(),
    )


@pytest.mark.django_db
def test_unoffered_nurse_cannot_list_or_read_pending_request(api_client: APIClient) -> None:
    """Nurses cannot enumerate pending requests unless they received an offer."""
    patient_user = create_patient(email="secure-patient@example.com")
    nurse_user = create_nurse(email="secure-unoffered@example.com")
    care_request = create_request(patient_user)
    authenticate(api_client, nurse_user)

    list_response = api_client.get(reverse("care-request-list"))
    detail_response = api_client.get(
        reverse("care-request-detail", kwargs={"request_id": care_request.id})
    )

    assert list_response.status_code == 200
    assert list_response.data == []
    assert detail_response.status_code == 404


@pytest.mark.django_db
def test_offered_nurse_receives_privacy_safe_request_payload(api_client: APIClient) -> None:
    """Pre-acceptance request payloads hide protected patient details from nurses."""
    patient_user = create_patient(email="safe-offer-patient@example.com")
    nurse_user = create_nurse(email="safe-offer-nurse@example.com")
    care_request = create_request(patient_user)
    RequestOffer.objects.create(
        care_request=care_request,
        nurse=nurse_user.nurse_profile,
        status=RequestOfferStatus.OFFERED,
        radius_km=10,
        distance_km="4.00",
        estimated_travel_time=9,
        specialization_match=True,
        rank=1,
        expires_at=timezone.now() + timedelta(minutes=2),
    )
    authenticate(api_client, nurse_user)

    response = api_client.get(
        reverse("care-request-detail", kwargs={"request_id": care_request.id})
    )

    assert response.status_code == 200
    assert response.data["patient_first_name"] == "Secure"
    assert response.data["patient_last_name"] == ""
    assert response.data["dependent_id"] is None
    assert response.data["dependent_name"] == ""
    assert response.data["description"] == ""
    assert response.data["requested_time"] is None


def test_secure_headers_and_jwt_settings_are_hardened() -> None:
    """Security settings enforce JWT rotation, scoped throttles, and browser headers."""
    assert settings.SIMPLE_JWT["ROTATE_REFRESH_TOKENS"] is True
    assert settings.SIMPLE_JWT["BLACKLIST_AFTER_ROTATION"] is True
    assert settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds() <= 900
    assert (
        "rest_framework.throttling.ScopedRateThrottle"
        in settings.REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"]
    )
    assert "auth_login" in settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]
    assert settings.SECURE_CONTENT_TYPE_NOSNIFF is True
    assert settings.X_FRAME_OPTIONS == "DENY"
    assert settings.SECURE_REFERRER_POLICY == "same-origin"
