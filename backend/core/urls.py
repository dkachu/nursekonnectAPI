"""Root URL configuration for the NurseKonnect API."""

from __future__ import annotations

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

from core.docs import openapi_schema, redoc_ui, swagger_ui


def health_check(_request: object) -> JsonResponse:
    """Return process health for load balancers and smoke tests."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz/", health_check, name="health-check"),
    path("api/schema/", openapi_schema, name="openapi-schema"),
    path("api/docs/swagger/", swagger_ui, name="swagger-ui"),
    path("api/docs/redoc/", redoc_ui, name="redoc-ui"),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/", include("apps.patients.urls")),
    path("api/", include("apps.nurses.urls")),
    path("api/", include("apps.tracking.urls")),
    path("api/", include("apps.requests.urls")),
    path("api/", include("apps.visits.urls")),
    path("api/", include("apps.ratings.urls")),
]
