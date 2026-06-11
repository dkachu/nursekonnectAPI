"""Final production readiness tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    """Return a DRF API client."""
    return APIClient()


def test_openapi_schema_and_docs_endpoints(api_client: APIClient) -> None:
    """OpenAPI, Swagger, and ReDoc endpoints are available."""
    schema_response = api_client.get(reverse("openapi-schema"))
    swagger_response = api_client.get(reverse("swagger-ui"))
    redoc_response = api_client.get(reverse("redoc-ui"))

    assert schema_response.status_code == 200
    assert schema_response["Content-Type"] == "application/yaml"
    assert "openapi: 3.0.3" in schema_response.content.decode()
    assert swagger_response.status_code == 200
    assert "/api/schema/" in swagger_response.content.decode()
    assert redoc_response.status_code == 200
    assert "/api/schema/" in redoc_response.content.decode()


def test_required_api_docs_exist() -> None:
    """Every implemented public API group has endpoint documentation."""
    docs_dir = Path(settings.BASE_DIR) / "api_docs"
    required_docs = {
        "accept_request.md",
        "admin_nurse_credential_review.md",
        "admin_nurse_reputation.md",
        "admin_nurse_verification.md",
        "auth_login.md",
        "auth_logout.md",
        "auth_refresh.md",
        "auth_register.md",
        "auth_resend_otp.md",
        "auth_verify_otp.md",
        "cancel_request.md",
        "complete_visit.md",
        "create_request.md",
        "list_requests.md",
        "location_update.md",
        "nearby_nurses.md",
        "nck_license_status_redirect.md",
        "nurse_availability.md",
        "nurse_credentials.md",
        "nurse_profile.md",
        "nurse_specializations.md",
        "nurse_status.md",
        "openapi_schema.md",
        "patient_dependents.md",
        "patient_emergency_contacts.md",
        "patient_medical_information.md",
        "patient_profile.md",
        "ratings.md",
        "redoc_ui.md",
        "request_arrived.md",
        "request_detail.md",
        "start_journey.md",
        "start_visit.md",
        "swagger_ui.md",
        "tracking_location.md",
        "visit_notes_create.md",
        "visit_notes_detail.md",
        "visit_notes_list.md",
    }

    missing = [doc for doc in sorted(required_docs) if not (docs_dir / doc).exists()]
    assert missing == []


def test_openapi_artifact_mentions_all_required_paths() -> None:
    """Static OpenAPI artifact covers the implemented API path surface."""
    schema_path = next(
        path
        for path in [
            settings.PROJECT_ROOT / "OPENAPI.yaml",
            settings.BASE_DIR / "OPENAPI.yaml",
        ]
        if path.exists()
    )
    schema = schema_path.read_text(encoding="utf-8")
    required_paths = [
        "/api/auth/register/",
        "/api/auth/login/",
        "/api/auth/refresh/",
        "/api/auth/logout/",
        "/api/auth/verify-otp/",
        "/api/auth/resend-otp/",
        "/api/patient/profile/",
        "/api/patient/emergency-contacts/",
        "/api/patient/dependents/",
        "/api/patients/{patient_id}/medical-information/",
        "/api/nurse/profile/",
        "/api/nurses/nearby/",
        "/api/location/update/",
        "/api/requests/",
        "/api/requests/{request_id}/accept/",
        "/api/requests/{request_id}/start-journey/",
        "/api/requests/{request_id}/arrived/",
        "/api/requests/{request_id}/start-visit/",
        "/api/requests/{request_id}/complete/",
        "/api/requests/{request_id}/cancel/",
        "/api/tracking/location/",
        "/api/visit-notes/",
        "/api/ratings/",
    ]

    missing = [path for path in required_paths if path not in schema]
    assert missing == []
