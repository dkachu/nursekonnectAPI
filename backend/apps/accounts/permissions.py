"""Role-based permission classes."""

from __future__ import annotations

from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.accounts.models import UserRole


class IsPatient(BasePermission):
    """Allow access to authenticated patients."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Return whether the current user is a patient."""
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == UserRole.PATIENT
        )


class IsNurse(BasePermission):
    """Allow access to authenticated nurses."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Return whether the current user is a nurse."""
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == UserRole.NURSE
        )


class IsAdmin(BasePermission):
    """Allow access to authenticated platform administrators."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Return whether the current user is an administrator."""
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == UserRole.ADMIN
        )


class IsOwner(BasePermission):
    """Allow object access when an object is owned by the current user."""

    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """Return whether the object or its user relation belongs to the requester."""
        owner = getattr(obj, "user", obj)
        return bool(request.user and request.user.is_authenticated and owner == request.user)
