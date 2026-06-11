"""Visit-domain authorization helpers."""

from __future__ import annotations

from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.accounts.models import UserRole
from apps.visits.models import VisitNote


class IsVisitMedicalActor(BasePermission):
    """Allow supported authenticated healthcare roles."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Return whether the authenticated user has a visit-supported role."""
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None)
            in {UserRole.PATIENT, UserRole.NURSE, UserRole.ADMIN}
        )


class IsVisitParticipantOrAdmin(BasePermission):
    """Object permission for patient owner, assigned nurse, or staff admin."""

    def has_object_permission(
        self,
        request: Request,
        view: APIView,
        obj: VisitNote,
    ) -> bool:
        """Return whether the actor can access a visit note."""
        role = getattr(request.user, "role", None)
        if role == UserRole.PATIENT:
            return obj.patient.user_id == request.user.id and request.method in SAFE_METHODS
        if role == UserRole.NURSE:
            return obj.nurse.user_id == request.user.id
        return role == UserRole.ADMIN and getattr(request.user, "is_staff", False)
