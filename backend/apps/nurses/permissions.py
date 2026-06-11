"""Nurse-domain permission classes."""

from __future__ import annotations

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.accounts.models import UserRole


class IsNurseUser(BasePermission):
    """Allow authenticated nurses to manage their own nurse resources."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Return whether the requester is an authenticated nurse."""
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == UserRole.NURSE
        )


class IsAuthorizedAdmin(BasePermission):
    """Allow staff administrators to perform compliance actions."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Return whether the requester is an authorized administrator."""
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == UserRole.ADMIN
            and getattr(request.user, "is_staff", False)
        )
