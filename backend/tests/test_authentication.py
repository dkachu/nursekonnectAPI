"""Authentication API and service tests."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

from apps.accounts.models import AuthenticationOTP, OTPPurpose, UserRole
from apps.accounts.permissions import IsAdmin, IsNurse, IsOwner, IsPatient
from apps.accounts.services.registration import RegistrationInput, RegistrationService
from apps.accounts.services.tokens import TokenService
from apps.accounts.services.verification import OTPService
from apps.accounts.views import (
    LoginView,
    RefreshView,
    RegisterView,
    ResendOTPView,
    VerifyOTPView,
)
from apps.audit_logs.models import AuditLog
from apps.nurses.models import NurseProfile, NurseVerificationStatus
from apps.patients.models import PatientProfile

User = get_user_model()


@pytest.fixture
def api_client() -> APIClient:
    """Return a DRF API client."""
    return APIClient()


@pytest.fixture
def patient_payload() -> dict[str, str]:
    """Return valid patient registration data."""
    return {
        "email": "patient@example.com",
        "password": "StrongPassword123!",
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+254712345678",
        "role": UserRole.PATIENT,
    }


@pytest.fixture
def nurse_payload() -> dict[str, str]:
    """Return valid nurse registration data."""
    return {
        "email": "nurse@example.com",
        "password": "StrongPassword123!",
        "first_name": "Jane",
        "last_name": "Wanjiku",
        "phone_number": "+254798765432",
        "role": UserRole.NURSE,
    }


@pytest.mark.django_db
def test_patient_registration_creates_user_profile_and_otps(
    api_client: APIClient,
    patient_payload: dict[str, str],
) -> None:
    """Patient registration creates the user, profile, and verification OTPs."""
    response = api_client.post(reverse("auth-register"), patient_payload, format="json")

    assert response.status_code == 201
    user = User.objects.get(email="patient@example.com")
    assert user.role == UserRole.PATIENT
    assert user.email_verified is False
    assert user.phone_verified is False
    assert PatientProfile.objects.filter(user=user, phone_number="+254712345678").exists()
    assert AuthenticationOTP.objects.filter(user=user, purpose=OTPPurpose.EMAIL).count() == 1
    assert AuthenticationOTP.objects.filter(user=user, purpose=OTPPurpose.PHONE).count() == 1
    assert AuditLog.objects.filter(action="AUTH_REGISTERED", actor=user).exists()


@pytest.mark.django_db
def test_nurse_registration_creates_pending_unavailable_profile(
    api_client: APIClient,
    nurse_payload: dict[str, str],
) -> None:
    """Nurse registration creates a pending unavailable nurse profile."""
    response = api_client.post(reverse("auth-register"), nurse_payload, format="json")

    assert response.status_code == 201
    user = User.objects.get(email="nurse@example.com")
    profile = NurseProfile.objects.get(user=user)
    assert user.role == UserRole.NURSE
    assert profile.phone_number == "+254798765432"
    assert profile.nck_verification_status == NurseVerificationStatus.PENDING
    assert profile.is_available is False


@pytest.mark.django_db
def test_registration_rejects_admin_role(
    api_client: APIClient,
    patient_payload: dict[str, str],
) -> None:
    """Public registration cannot create administrator accounts."""
    patient_payload["role"] = UserRole.ADMIN

    response = api_client.post(reverse("auth-register"), patient_payload, format="json")

    assert response.status_code == 400
    assert User.objects.count() == 0


@pytest.mark.django_db
def test_registration_rejects_duplicate_email(
    api_client: APIClient,
    patient_payload: dict[str, str],
) -> None:
    """Email addresses are unique."""
    api_client.post(reverse("auth-register"), patient_payload, format="json")

    response = api_client.post(reverse("auth-register"), patient_payload, format="json")

    assert response.status_code == 400
    assert "email" in response.data


@pytest.mark.django_db
def test_registration_rejects_invalid_phone(
    api_client: APIClient,
    patient_payload: dict[str, str],
) -> None:
    """Phone numbers must use Kenyan E.164 format."""
    patient_payload["phone_number"] = "0712345678"

    response = api_client.post(reverse("auth-register"), patient_payload, format="json")

    assert response.status_code == 400
    assert "phone_number" in response.data


@pytest.mark.django_db
def test_login_returns_token_pair(api_client: APIClient, patient_payload: dict[str, str]) -> None:
    """A valid email/password login returns access, refresh, and user metadata."""
    api_client.post(reverse("auth-register"), patient_payload, format="json")

    response = api_client.post(
        reverse("auth-login"),
        {"email": patient_payload["email"], "password": patient_payload["password"]},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["access"]
    assert response.data["refresh"]
    assert response.data["user"]["email"] == patient_payload["email"]
    assert AuditLog.objects.filter(action="AUTH_LOGIN_SUCCEEDED").exists()


@pytest.mark.django_db
def test_login_rejects_invalid_credentials(api_client: APIClient) -> None:
    """Invalid credentials return an authentication error."""
    response = api_client.post(
        reverse("auth-login"),
        {"email": "missing@example.com", "password": "wrong"},
        format="json",
    )

    assert response.status_code == 401
    assert AuditLog.objects.filter(action="AUTH_LOGIN_FAILED").exists()


@pytest.mark.django_db
def test_refresh_rotates_token(api_client: APIClient, patient_payload: dict[str, str]) -> None:
    """Refresh endpoint returns a new access and refresh token."""
    api_client.post(reverse("auth-register"), patient_payload, format="json")
    login_response = api_client.post(
        reverse("auth-login"),
        {"email": patient_payload["email"], "password": patient_payload["password"]},
        format="json",
    )

    response = api_client.post(
        reverse("auth-refresh"),
        {"refresh": login_response.data["refresh"]},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["access"]
    assert response.data["refresh"]
    assert response.data["refresh"] != login_response.data["refresh"]


@pytest.mark.django_db
def test_refresh_rejects_invalid_token(api_client: APIClient) -> None:
    """Invalid refresh tokens are rejected."""
    response = api_client.post(reverse("auth-refresh"), {"refresh": "not-a-token"}, format="json")

    assert response.status_code == 400


@pytest.mark.django_db
def test_logout_blacklists_refresh_token(
    api_client: APIClient,
    patient_payload: dict[str, str],
) -> None:
    """Logout blacklists the submitted refresh token."""
    api_client.post(reverse("auth-register"), patient_payload, format="json")
    login_response = api_client.post(
        reverse("auth-login"),
        {"email": patient_payload["email"], "password": patient_payload["password"]},
        format="json",
    )
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")

    response = api_client.post(
        reverse("auth-logout"),
        {"refresh": login_response.data["refresh"]},
        format="json",
    )

    assert response.status_code == 204
    assert BlacklistedToken.objects.count() == 1
    assert AuditLog.objects.filter(action="AUTH_LOGGED_OUT").exists()


@pytest.mark.django_db
def test_logout_requires_authentication(api_client: APIClient) -> None:
    """Anonymous users cannot logout tokens."""
    response = api_client.post(reverse("auth-logout"), {"refresh": "x"}, format="json")

    assert response.status_code == 401


@pytest.mark.django_db
def test_verify_email_otp_marks_user_verified(
    api_client: APIClient,
    patient_payload: dict[str, str],
) -> None:
    """A valid email OTP marks the user's email as verified."""
    with patch("apps.accounts.services.verification.secrets.randbelow", return_value=123456):
        api_client.post(reverse("auth-register"), patient_payload, format="json")
    login_response = api_client.post(
        reverse("auth-login"),
        {"email": patient_payload["email"], "password": patient_payload["password"]},
        format="json",
    )
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")

    response = api_client.post(
        reverse("auth-verify-otp"),
        {"purpose": OTPPurpose.EMAIL, "code": "123456"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["user"]["email_verified"] is True
    assert User.objects.get(email=patient_payload["email"]).email_verified is True
    assert AuditLog.objects.filter(action="AUTH_OTP_VERIFIED").exists()


@pytest.mark.django_db
def test_verify_otp_rejects_bad_code(
    api_client: APIClient,
    patient_payload: dict[str, str],
) -> None:
    """Invalid OTP codes are rejected."""
    with patch("apps.accounts.services.verification.secrets.randbelow", return_value=123456):
        api_client.post(reverse("auth-register"), patient_payload, format="json")
    login_response = api_client.post(
        reverse("auth-login"),
        {"email": patient_payload["email"], "password": patient_payload["password"]},
        format="json",
    )
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")

    response = api_client.post(
        reverse("auth-verify-otp"),
        {"purpose": OTPPurpose.EMAIL, "code": "654321"},
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_resend_otp_consumes_previous_code(
    api_client: APIClient,
    patient_payload: dict[str, str],
) -> None:
    """Resending an OTP invalidates previous unconsumed OTPs for that purpose."""
    api_client.post(reverse("auth-register"), patient_payload, format="json")
    user = User.objects.get(email=patient_payload["email"])
    old_otp = AuthenticationOTP.objects.filter(user=user, purpose=OTPPurpose.PHONE).latest(
        "created_at"
    )
    login_response = api_client.post(
        reverse("auth-login"),
        {"email": patient_payload["email"], "password": patient_payload["password"]},
        format="json",
    )
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")

    response = api_client.post(
        reverse("auth-resend-otp"),
        {"purpose": OTPPurpose.PHONE},
        format="json",
    )

    old_otp.refresh_from_db()
    assert response.status_code == 200
    assert old_otp.consumed_at is not None
    assert AuthenticationOTP.objects.filter(user=user, purpose=OTPPurpose.PHONE).count() == 2
    assert AuditLog.objects.filter(action="AUTH_OTP_RESENT").exists()


@pytest.mark.django_db
def test_verify_phone_otp_marks_user_verified(
    api_client: APIClient,
    patient_payload: dict[str, str],
) -> None:
    """A valid phone OTP marks the user's phone as verified."""
    with patch("apps.accounts.services.verification.secrets.randbelow", return_value=222222):
        api_client.post(reverse("auth-register"), patient_payload, format="json")
    login_response = api_client.post(
        reverse("auth-login"),
        {"email": patient_payload["email"], "password": patient_payload["password"]},
        format="json",
    )
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")

    response = api_client.post(
        reverse("auth-verify-otp"),
        {"purpose": OTPPurpose.PHONE, "code": "222222"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["user"]["phone_verified"] is True


@pytest.mark.django_db
def test_logout_rejects_invalid_refresh_for_authenticated_user(
    api_client: APIClient,
    patient_payload: dict[str, str],
) -> None:
    """Logout maps invalid refresh token failures to a validation error."""
    api_client.post(reverse("auth-register"), patient_payload, format="json")
    login_response = api_client.post(
        reverse("auth-login"),
        {"email": patient_payload["email"], "password": patient_payload["password"]},
        format="json",
    )
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")

    response = api_client.post(reverse("auth-logout"), {"refresh": "bad-token"}, format="json")

    assert response.status_code == 400


@pytest.mark.django_db
def test_register_view_maps_service_error(
    api_client: APIClient,
    patient_payload: dict[str, str],
) -> None:
    """Registration view maps service ValueErrors to validation responses."""
    with patch(
        "apps.accounts.views.RegistrationService.register",
        side_effect=ValueError("service failure"),
    ):
        response = api_client.post(reverse("auth-register"), patient_payload, format="json")

    assert response.status_code == 400
    assert response.data["detail"] == "service failure"


@pytest.mark.django_db
def test_resend_view_maps_service_error(
    api_client: APIClient,
    patient_payload: dict[str, str],
) -> None:
    """Resend view maps service ValueErrors to validation responses."""
    api_client.post(reverse("auth-register"), patient_payload, format="json")
    login_response = api_client.post(
        reverse("auth-login"),
        {"email": patient_payload["email"], "password": patient_payload["password"]},
        format="json",
    )
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")
    with patch(
        "apps.accounts.views.OTPService.resend_otp",
        side_effect=ValueError("service failure"),
    ):
        response = api_client.post(
            reverse("auth-resend-otp"),
            {"purpose": OTPPurpose.EMAIL},
            format="json",
        )

    assert response.status_code == 400
    assert response.data["detail"] == "service failure"


@pytest.mark.django_db
def test_registration_service_rejects_admin_role() -> None:
    """The service layer also protects against public admin creation."""
    data = RegistrationInput(
        email="admin@example.com",
        password="StrongPassword123!",
        first_name="Ada",
        last_name="Admin",
        phone_number="+254700000000",
        role=UserRole.ADMIN,
    )

    with pytest.raises(ValueError, match="Only patient and nurse"):
        RegistrationService().register(data)


@pytest.mark.django_db
def test_user_manager_validation_branches() -> None:
    """User manager validates required email and superuser flags."""
    with pytest.raises(ValueError, match="email"):
        User.objects.create_user(email="", password="StrongPassword123!")
    with pytest.raises(ValueError, match="is_staff"):
        User.objects.create_superuser(
            email="badstaff@example.com",
            password="StrongPassword123!",
            is_staff=False,
        )
    with pytest.raises(ValueError, match="is_superuser"):
        User.objects.create_superuser(
            email="badsuper@example.com",
            password="StrongPassword123!",
            is_superuser=False,
        )
    with pytest.raises(ValueError, match="role=ADMIN"):
        User.objects.create_superuser(
            email="badrole@example.com",
            password="StrongPassword123!",
            role=UserRole.PATIENT,
        )
    admin = User.objects.create_superuser(
        email="admin@example.com",
        password="StrongPassword123!",
        first_name="Ada",
        last_name="Admin",
    )
    assert admin.is_staff is True
    assert admin.is_superuser is True
    assert admin.email_verified is True
    assert admin.phone_verified is True


@pytest.mark.django_db
def test_user_and_profile_string_helpers() -> None:
    """Model string helpers return stable readable labels."""
    patient = User.objects.create_user(
        email="string-patient@example.com",
        password="StrongPassword123!",
        first_name="String",
        last_name="Patient",
        role=UserRole.PATIENT,
    )
    nurse = User.objects.create_user(
        email="string-nurse@example.com",
        password="StrongPassword123!",
        first_name="String",
        last_name="Nurse",
        role=UserRole.NURSE,
    )
    patient_profile = PatientProfile.objects.create(user=patient, phone_number="+254700000001")
    nurse_profile = NurseProfile.objects.create(user=nurse, phone_number="+254700000002")

    assert str(patient) == "string-patient@example.com"
    assert patient.full_name == "String Patient"
    assert str(patient_profile) == f"PatientProfile<{patient.id}>"
    assert str(nurse_profile) == f"NurseProfile<{nurse.id}>"


@pytest.mark.django_db
def test_otp_service_rejects_expired_code() -> None:
    """Expired OTPs cannot verify users."""
    user = User.objects.create_user(
        email="expired@example.com",
        password="StrongPassword123!",
        first_name="Old",
        last_name="Code",
        role=UserRole.PATIENT,
    )
    with patch("apps.accounts.services.verification.secrets.randbelow", return_value=111111):
        OTPService().create_otp(user=user, purpose=OTPPurpose.EMAIL)
    AuthenticationOTP.objects.filter(user=user).update(expires_at=timezone.now())

    with pytest.raises(ValueError, match="Invalid or expired OTP"):
        OTPService().verify_otp(user=user, purpose=OTPPurpose.EMAIL, code="111111")


@pytest.mark.django_db
def test_otp_helpers_and_unsupported_purpose() -> None:
    """OTP model helpers and service purpose validation behave correctly."""
    user = User.objects.create_user(
        email="otp-helper@example.com",
        password="StrongPassword123!",
        first_name="Otp",
        last_name="Helper",
        role=UserRole.PATIENT,
    )
    result = OTPService().create_otp(user=user, purpose=OTPPurpose.EMAIL)
    otp = AuthenticationOTP.objects.get(user=user)

    assert len(result.code) == 6
    assert otp.is_consumed is False
    assert otp.is_expired is False
    with pytest.raises(ValueError, match="Unsupported OTP purpose"):
        OTPService().create_otp(user=user, purpose="FAX")


@pytest.mark.django_db
def test_token_service_rejects_inactive_user() -> None:
    """Inactive users cannot authenticate."""
    User.objects.create_user(
        email="inactive@example.com",
        password="StrongPassword123!",
        first_name="Inactive",
        last_name="User",
        role=UserRole.PATIENT,
        is_active=False,
    )

    with pytest.raises(ValueError, match="Invalid email or password|inactive"):
        TokenService().authenticate("inactive@example.com", "StrongPassword123!")


@pytest.mark.django_db
def test_token_service_inactive_branch() -> None:
    """Token service rejects authenticated inactive user objects."""
    inactive_user = User(
        email="inactive-branch@example.com",
        first_name="Inactive",
        last_name="Branch",
        role=UserRole.PATIENT,
        is_active=False,
    )
    with patch("apps.accounts.services.tokens.authenticate", return_value=inactive_user):
        with pytest.raises(ValueError, match="inactive"):
            TokenService().authenticate("inactive-branch@example.com", "StrongPassword123!")


def test_token_service_blacklist_rejects_invalid_token() -> None:
    """Token service maps invalid blacklist token errors."""
    with pytest.raises(ValueError, match="Invalid refresh token"):
        TokenService().blacklist("bad-token")


def test_role_permissions() -> None:
    """Role permissions rely on user.role instead of staff flags."""

    class Anonymous:
        is_authenticated = False
        role = None

    class Request:
        def __init__(self, role: str | None) -> None:
            self.user = Anonymous()
            if role:
                self.user.is_authenticated = True
                self.user.role = role

    assert IsPatient().has_permission(Request(UserRole.PATIENT), None) is True
    assert IsPatient().has_permission(Request(UserRole.NURSE), None) is False
    assert IsNurse().has_permission(Request(UserRole.NURSE), None) is True
    assert IsAdmin().has_permission(Request(UserRole.ADMIN), None) is False
    assert IsAdmin().has_permission(Request(None), None) is False


def test_auth_views_use_scoped_throttles() -> None:
    """Authentication endpoints use dedicated abuse-control throttle scopes."""
    assert RegisterView.throttle_scope == "auth_register"
    assert LoginView.throttle_scope == "auth_login"
    assert RefreshView.throttle_scope == "auth_refresh"
    assert VerifyOTPView.throttle_scope == "otp_verify"
    assert ResendOTPView.throttle_scope == "otp_resend"


def test_owner_permission() -> None:
    """Owner permission supports direct user objects and objects with user relation."""

    class Owner:
        is_authenticated = True

    owner = Owner()

    class Request:
        user = owner

    class OwnedObject:
        user = owner

    assert IsOwner().has_object_permission(Request(), None, owner) is True
    assert IsOwner().has_object_permission(Request(), None, OwnedObject()) is True
