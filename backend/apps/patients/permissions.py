"""Patient-domain authorization helpers."""

from __future__ import annotations

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.accounts.models import UserRole


class IsPatientUser(BasePermission):
    """Allow authenticated patients only."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Return whether the request user is a patient."""
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == UserRole.PATIENT
        )


class IsPatientMedicalActor(BasePermission):
    """Allow authenticated users who may request medical-data access checks."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Return whether the user has a supported healthcare role."""
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None)
            in {UserRole.PATIENT, UserRole.NURSE, UserRole.ADMIN}
        )
