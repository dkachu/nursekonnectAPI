"""NCK external verification service."""

from __future__ import annotations

from django.conf import settings


class NCKVerificationPortalService:
    """Expose the configured external NCK license verification portal."""

    def verification_url(self) -> str:
        """Return the official NCK license status URL."""
        return settings.NCK_LICENSE_STATUS_URL
