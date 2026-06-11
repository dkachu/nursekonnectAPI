"""Nurse credential service operations."""

from __future__ import annotations

from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import UserRole
from apps.nurses.models import NurseCredential, NurseProfile


class NurseCredentialService:
    """Create and review nurse credential uploads."""

    @transaction.atomic
    def create(
        self,
        *,
        actor: object,
        nurse: NurseProfile,
        data: dict[str, Any],
    ) -> NurseCredential:
        """Create a credential image owned by a nurse."""
        if nurse.user_id != getattr(actor, "id", None):
            raise PermissionError("You can only upload credentials for your own nurse profile.")
        return NurseCredential.objects.create(nurse=nurse, **data)

    @transaction.atomic
    def review(
        self,
        *,
        actor: object,
        credential: NurseCredential,
        data: dict[str, Any],
    ) -> NurseCredential:
        """Review a nurse credential as an administrator."""
        if getattr(actor, "role", None) != UserRole.ADMIN or not getattr(actor, "is_staff", False):
            raise PermissionError("Only authorized administrators can review credentials.")

        credential.verification_status = data["verification_status"]
        credential.review_notes = data.get("review_notes", credential.review_notes)
        credential.reviewed_by = actor
        credential.reviewed_at = timezone.now()
        credential.save(
            update_fields=[
                "verification_status",
                "review_notes",
                "reviewed_by",
                "reviewed_at",
                "updated_at",
            ]
        )
        return credential
