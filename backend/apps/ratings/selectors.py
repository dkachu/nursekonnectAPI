"""Optimized rating selectors."""

from __future__ import annotations

from django.db.models import QuerySet

from apps.accounts.models import UserRole
from apps.ratings.models import Rating


class RatingSelector:
    """Read ratings using role-aware object boundaries."""

    def base_queryset(self) -> QuerySet[Rating]:
        """Return ratings with related data needed by serializers."""
        return (
            Rating.objects.select_related(
                "patient",
                "patient__user",
                "nurse",
                "nurse__user",
                "care_request",
            )
            .filter(is_deleted=False)
            .order_by("-created_at")
        )

    def for_actor(self, actor: object) -> QuerySet[Rating]:
        """Return ratings visible to an actor."""
        role = getattr(actor, "role", None)
        queryset = self.base_queryset()
        if role == UserRole.PATIENT:
            return queryset.filter(patient__user=actor)
        if role == UserRole.NURSE:
            return queryset.filter(nurse__user=actor)
        if role == UserRole.ADMIN and getattr(actor, "is_staff", False):
            return queryset
        return queryset.none()
