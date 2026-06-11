"""Foundation smoke tests."""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase
from django.urls import reverse


class FoundationConfigurationTests(SimpleTestCase):
    """Validate foundation settings without touching the database."""

    def test_custom_user_model_is_configured(self) -> None:
        """The project uses the email-only accounts user model."""
        self.assertEqual(settings.AUTH_USER_MODEL, "accounts.User")
        self.assertEqual(get_user_model().USERNAME_FIELD, "email")

    def test_health_route_is_registered(self) -> None:
        """The health check route resolves for deployment smoke tests."""
        self.assertEqual(reverse("health-check"), "/healthz/")

    def test_health_endpoint_returns_ok(self) -> None:
        """The app responds successfully to health checks."""
        response = self.client.get("/healthz/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_postgis_database_backend_is_configured(self) -> None:
        """The production database is configured for PostGIS."""
        engine = settings.DATABASES["default"]["ENGINE"]
        self.assertEqual(engine, "django.contrib.gis.db.backends.postgis")
