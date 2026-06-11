"""Nurse-domain tests."""

from __future__ import annotations

from datetime import date, time
from decimal import Decimal
from io import BytesIO

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from PIL import Image
from rest_framework.test import APIClient

from apps.accounts.models import UserRole
from apps.accounts.services.tokens import TokenService
from apps.nurses.models import (
    CredentialType,
    DayOfWeek,
    NurseAvailabilitySlot,
    NurseCredential,
    NurseProfile,
    NurseSpecialization,
    NurseStatus,
    NurseVerificationStatus,
    TravelRadiusKm,
)
from apps.nurses.permissions import IsAuthorizedAdmin, IsNurseUser
from apps.nurses.services.reputation import NurseReputationService
from apps.nurses.services.status import NurseStatusService

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
def nurse_user() -> object:
    """Create a nurse user and profile."""
    user = User.objects.create_user(
        email="nurse-domain@example.com",
        password="StrongPassword123!",
        first_name="Nurse",
        last_name="Domain",
        role=UserRole.NURSE,
    )
    NurseProfile.objects.create(user=user, phone_number="+254700000020")
    return user


@pytest.fixture
def patient_user() -> object:
    """Create a patient user."""
    return User.objects.create_user(
        email="nurse-domain-patient@example.com",
        password="StrongPassword123!",
        first_name="Patient",
        last_name="Domain",
        role=UserRole.PATIENT,
    )


@pytest.fixture
def admin_user() -> object:
    """Create an authorized admin user."""
    return User.objects.create_superuser(
        email="nurse-domain-admin@example.com",
        password="StrongPassword123!",
        first_name="Admin",
        last_name="Domain",
    )


def uploaded_image(name: str = "credential.png") -> SimpleUploadedFile:
    """Return a tiny valid uploaded PNG image."""
    image = Image.new("RGB", (1, 1), color="white")
    image_file = BytesIO()
    image.save(image_file, format="PNG")
    return SimpleUploadedFile(name, image_file.getvalue(), content_type="image/png")


def test_nck_license_status_redirect_is_public(api_client: APIClient) -> None:
    """Users can be redirected to the official NCK license status page."""
    response = api_client.get(reverse("nck-license-status-redirect"))

    assert response.status_code == 302
    assert response.url == "https://osp.nckenya.com/LicenseStatus"


@pytest.mark.django_db
def test_nurse_can_patch_and_read_profile(api_client: APIClient, nurse_user: object) -> None:
    """Nurse can manage own profile fields."""
    authenticate(api_client, nurse_user)

    patch_response = api_client.patch(
        reverse("nurse-profile"),
        {
            "national_id": "98765432",
            "gender": "FEMALE",
            "date_of_birth": "1988-01-01",
            "years_of_experience": 8,
            "bio": "Home care and wound care nurse",
            "county": "Nairobi",
            "address": "Kilimani",
            "travel_radius_km": TravelRadiusKm.FIFTY,
        },
        format="json",
    )
    get_response = api_client.get(reverse("nurse-profile"))

    assert patch_response.status_code == 200
    assert patch_response.data["travel_radius_km"] == TravelRadiusKm.FIFTY
    assert get_response.data["bio"] == "Home care and wound care nurse"


@pytest.mark.django_db
def test_patient_cannot_use_nurse_profile_endpoint(
    api_client: APIClient,
    patient_user: object,
) -> None:
    """Patient role is rejected by nurse-owned endpoints."""
    authenticate(api_client, patient_user)

    response = api_client.get(reverse("nurse-profile"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_specialization_catalog_and_update(
    api_client: APIClient,
    nurse_user: object,
) -> None:
    """Nurses can list and set supported specializations."""
    authenticate(api_client, nurse_user)

    list_response = api_client.get(reverse("nurse-specialization-list"))
    update_response = api_client.put(
        reverse("nurse-specialization-update"),
        {"specializations": ["GENERAL_NURSING", "WOUND_CARE"]},
        format="json",
    )
    invalid_response = api_client.put(
        reverse("nurse-specialization-update"),
        {"specializations": ["NOT_REAL"]},
        format="json",
    )

    assert list_response.status_code == 200
    assert len(list_response.data) == 10
    assert update_response.status_code == 200
    assert {item["code"] for item in update_response.data["specializations"]} == {
        "GENERAL_NURSING",
        "WOUND_CARE",
    }
    assert invalid_response.status_code == 400


@pytest.mark.django_db
def test_nurse_can_upload_credential_image(api_client: APIClient, nurse_user: object) -> None:
    """Nurses can upload credential images for admin review."""
    authenticate(api_client, nurse_user)

    response = api_client.post(
        reverse("nurse-credential-list"),
        {
            "credential_type": CredentialType.NCK_LICENSE,
            "image": uploaded_image(),
        },
        format="multipart",
    )
    list_response = api_client.get(reverse("nurse-credential-list"))

    assert response.status_code == 201
    assert response.data["verification_status"] == NurseVerificationStatus.PENDING
    assert NurseCredential.objects.count() == 1
    assert len(list_response.data) == 1


@pytest.mark.django_db
def test_admin_can_review_credential(
    api_client: APIClient,
    nurse_user: object,
    admin_user: object,
) -> None:
    """Authorized admins can review credential uploads."""
    credential = NurseCredential.objects.create(
        nurse=nurse_user.nurse_profile,
        credential_type=CredentialType.NATIONAL_ID,
        image=uploaded_image("id.png"),
    )
    authenticate(api_client, admin_user)

    response = api_client.patch(
        reverse(
            "admin-nurse-credential-review",
            kwargs={"nurse_id": nurse_user.nurse_profile.id, "credential_id": credential.id},
        ),
        {
            "verification_status": NurseVerificationStatus.VERIFIED,
            "review_notes": "Valid ID",
        },
        format="json",
    )

    credential.refresh_from_db()
    assert response.status_code == 200
    assert credential.verification_status == NurseVerificationStatus.VERIFIED
    assert credential.reviewed_by == admin_user
    assert credential.review_notes == "Valid ID"


@pytest.mark.django_db
def test_admin_can_list_nurses_and_selected_credentials(
    api_client: APIClient,
    nurse_user: object,
    admin_user: object,
) -> None:
    """Authorized admins can load nurse verification dashboard data."""
    credential = NurseCredential.objects.create(
        nurse=nurse_user.nurse_profile,
        credential_type=CredentialType.NCK_LICENSE,
        image=uploaded_image("license.png"),
    )
    authenticate(api_client, admin_user)

    nurses_response = api_client.get(reverse("admin-nurse-list"))
    credentials_response = api_client.get(
        reverse(
            "admin-nurse-credential-list",
            kwargs={"nurse_id": nurse_user.nurse_profile.id},
        )
    )

    assert nurses_response.status_code == 200
    assert nurses_response.data[0]["id"] == nurse_user.nurse_profile.id
    assert credentials_response.status_code == 200
    assert credentials_response.data[0]["id"] == credential.id


@pytest.mark.django_db
def test_patient_cannot_load_admin_nurse_dashboard(
    api_client: APIClient,
    patient_user: object,
) -> None:
    """Non-admin actors cannot enumerate verification dashboard data."""
    authenticate(api_client, patient_user)

    response = api_client.get(reverse("admin-nurse-list"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_nurse_can_manage_availability(api_client: APIClient, nurse_user: object) -> None:
    """Nurses can create, list, update, and delete availability slots."""
    authenticate(api_client, nurse_user)

    create_response = api_client.post(
        reverse("nurse-availability-list"),
        {"day_of_week": DayOfWeek.MONDAY, "start_time": "08:00", "end_time": "17:00"},
        format="json",
    )
    slot_id = create_response.data["id"]
    list_response = api_client.get(reverse("nurse-availability-list"))
    update_response = api_client.patch(
        reverse("nurse-availability-detail", kwargs={"slot_id": slot_id}),
        {"end_time": "18:00"},
        format="json",
    )
    delete_response = api_client.delete(
        reverse("nurse-availability-detail", kwargs={"slot_id": slot_id})
    )

    assert create_response.status_code == 201
    assert len(list_response.data) == 1
    assert update_response.data["end_time"] == "18:00:00"
    assert delete_response.status_code == 204
    assert NurseAvailabilitySlot.objects.count() == 0


@pytest.mark.django_db
def test_availability_rejects_invalid_time_window(
    api_client: APIClient,
    nurse_user: object,
) -> None:
    """Availability windows must end after they start."""
    authenticate(api_client, nurse_user)

    response = api_client.post(
        reverse("nurse-availability-list"),
        {"day_of_week": DayOfWeek.TUESDAY, "start_time": "17:00", "end_time": "08:00"},
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_admin_verification_controls_platform_availability(
    api_client: APIClient,
    nurse_user: object,
    admin_user: object,
) -> None:
    """NCK verification only enables availability when account verification is complete."""
    nurse_user.email_verified = True
    nurse_user.phone_verified = True
    nurse_user.save(update_fields=["email_verified", "phone_verified", "updated_at"])
    authenticate(api_client, admin_user)

    response = api_client.patch(
        reverse("admin-nurse-verification", kwargs={"nurse_id": nurse_user.nurse_profile.id}),
        {
            "nck_license_number": "NCK-12345",
            "nck_license_expiry": "2030-01-01",
            "nck_verification_status": NurseVerificationStatus.VERIFIED,
        },
        format="json",
    )

    nurse_user.nurse_profile.refresh_from_db()
    assert response.status_code == 200
    assert response.data["nck_verification_status"] == NurseVerificationStatus.VERIFIED
    assert nurse_user.nurse_profile.is_available is True


@pytest.mark.django_db
def test_verification_requires_future_license_expiry(
    api_client: APIClient,
    nurse_user: object,
    admin_user: object,
) -> None:
    """Admins cannot verify an expired NCK license."""
    authenticate(api_client, admin_user)

    response = api_client.patch(
        reverse("admin-nurse-verification", kwargs={"nurse_id": nurse_user.nurse_profile.id}),
        {
            "nck_license_number": "NCK-EXPIRED",
            "nck_license_expiry": "2020-01-01",
            "nck_verification_status": NurseVerificationStatus.VERIFIED,
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_non_staff_admin_cannot_verify_nurse(
    api_client: APIClient,
    nurse_user: object,
) -> None:
    """Admin role without staff authorization cannot verify nurses."""
    non_staff_admin = User.objects.create_user(
        email="nurse-nonstaff-admin@example.com",
        password="StrongPassword123!",
        first_name="Nonstaff",
        last_name="Admin",
        role=UserRole.ADMIN,
        is_staff=False,
    )
    authenticate(api_client, non_staff_admin)

    response = api_client.patch(
        reverse("admin-nurse-verification", kwargs={"nurse_id": nurse_user.nurse_profile.id}),
        {"nck_verification_status": NurseVerificationStatus.UNDER_REVIEW},
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_nurse_status_requires_platform_availability(
    api_client: APIClient,
    nurse_user: object,
) -> None:
    """Unverified nurses cannot go online."""
    authenticate(api_client, nurse_user)

    response = api_client.post(
        reverse("nurse-status"),
        {"status": NurseStatus.ONLINE, "location_visible": True},
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_verified_nurse_can_go_online_and_busy_hides_location(
    api_client: APIClient,
    nurse_user: object,
) -> None:
    """Verified nurses can go online, and busy status disables visibility."""
    nurse = nurse_user.nurse_profile
    nurse_user.email_verified = True
    nurse_user.phone_verified = True
    nurse_user.save(update_fields=["email_verified", "phone_verified", "updated_at"])
    nurse.nck_verification_status = NurseVerificationStatus.VERIFIED
    nurse.nck_license_number = "NCK-ONLINE"
    nurse.nck_license_expiry = date(2030, 1, 1)
    nurse.save()
    NurseStatusService().refresh_platform_availability(nurse)
    authenticate(api_client, nurse_user)

    online_response = api_client.post(
        reverse("nurse-status"),
        {"status": NurseStatus.ONLINE, "location_visible": True},
        format="json",
    )
    busy_response = api_client.post(
        reverse("nurse-status"),
        {"status": NurseStatus.BUSY, "location_visible": True},
        format="json",
    )

    assert online_response.status_code == 200
    assert online_response.data["location_visible"] is True
    assert busy_response.status_code == 200
    assert busy_response.data["status"] == NurseStatus.BUSY
    assert busy_response.data["location_visible"] is False


@pytest.mark.django_db
def test_expired_license_disables_availability(nurse_user: object) -> None:
    """Expired NCK licenses disable request availability."""
    nurse = nurse_user.nurse_profile
    nurse_user.email_verified = True
    nurse_user.phone_verified = True
    nurse_user.save(update_fields=["email_verified", "phone_verified", "updated_at"])
    nurse.nck_verification_status = NurseVerificationStatus.VERIFIED
    nurse.nck_license_number = "NCK-OLD"
    nurse.nck_license_expiry = timezone.localdate().replace(year=timezone.localdate().year - 1)
    nurse.is_available = True
    nurse.status = NurseStatus.ONLINE
    nurse.location_visible = True
    nurse.save()

    NurseStatusService().refresh_platform_availability(nurse)
    nurse.refresh_from_db()

    assert nurse.license_is_expired is True
    assert nurse.is_available is False
    assert nurse.status == NurseStatus.OFFLINE
    assert nurse.location_visible is False


@pytest.mark.django_db
def test_reputation_score_can_be_recalculated(
    api_client: APIClient,
    nurse_user: object,
    admin_user: object,
) -> None:
    """Reputation score combines rating, completion rate, and response speed."""
    nurse = nurse_user.nurse_profile
    nurse.rating = Decimal("4.50")
    nurse.completed_visits_count = 18
    nurse.cancelled_visits_count = 2
    nurse.average_response_seconds = 120
    nurse.save()
    authenticate(api_client, admin_user)

    response = api_client.post(
        reverse("admin-nurse-reputation-recalculate", kwargs={"nurse_id": nurse.id})
    )

    nurse.refresh_from_db()
    assert response.status_code == 200
    assert nurse.reputation_score > Decimal("80.00")


@pytest.mark.django_db
def test_reputation_service_zero_inputs(nurse_user: object) -> None:
    """A nurse without reputation inputs receives a zero score."""
    nurse = NurseReputationService().recalculate(nurse=nurse_user.nurse_profile)

    assert nurse.reputation_score == Decimal("0.00")


def test_nurse_domain_permissions() -> None:
    """Nurse and authorized admin permissions use roles correctly."""

    class Anonymous:
        is_authenticated = False
        role = None
        is_staff = False

    class Request:
        def __init__(self, role: str | None, *, is_staff: bool = False) -> None:
            self.user = Anonymous()
            if role:
                self.user.is_authenticated = True
                self.user.role = role
                self.user.is_staff = is_staff

    assert IsNurseUser().has_permission(Request(UserRole.NURSE), None) is True
    assert IsNurseUser().has_permission(Request(UserRole.PATIENT), None) is False
    assert IsAuthorizedAdmin().has_permission(Request(UserRole.ADMIN, is_staff=True), None) is True
    assert (
        IsAuthorizedAdmin().has_permission(Request(UserRole.ADMIN, is_staff=False), None) is False
    )


@pytest.mark.django_db
def test_model_string_helpers(nurse_user: object) -> None:
    """Nurse model string helpers return stable readable labels."""
    specialization = NurseSpecialization.objects.get(code="GENERAL_NURSING")
    credential = NurseCredential.objects.create(
        nurse=nurse_user.nurse_profile,
        credential_type=CredentialType.PASSPORT_PHOTO,
        image=uploaded_image("passport.png"),
    )
    slot = NurseAvailabilitySlot.objects.create(
        nurse=nurse_user.nurse_profile,
        day_of_week=DayOfWeek.FRIDAY,
        start_time=time(8, 0),
        end_time=time(12, 0),
    )

    assert str(specialization) == "GENERAL_NURSING"
    assert str(credential) == f"NurseCredential<{nurse_user.nurse_profile.id}:PASSPORT_PHOTO>"
    assert str(slot) == f"NurseAvailabilitySlot<{nurse_user.nurse_profile.id}:5>"
