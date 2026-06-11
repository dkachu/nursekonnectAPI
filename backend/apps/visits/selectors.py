"""Optimized visit note selectors."""

from __future__ import annotations

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from apps.accounts.models import UserRole
from apps.visits.models import VisitNote


class VisitNoteSelector:
    """Read visit notes using healthcare object boundaries."""

    def base_queryset(self) -> QuerySet[VisitNote]:
        """Return visit notes with related data needed by serializers and permissions."""
        return (
            VisitNote.objects.select_related(
                "care_request",
                "patient",
                "patient__user",
                "nurse",
                "nurse__user",
            )
            .filter(is_deleted=False)
            .order_by("-created_at")
        )

    def for_actor(self, actor: object) -> QuerySet[VisitNote]:
        """Return notes visible to patient owner, assigned nurse, or staff admin."""
        role = getattr(actor, "role", None)
        queryset = self.base_queryset()

        if role == UserRole.PATIENT:
            return queryset.filter(patient__user=actor)

        if role == UserRole.NURSE:
            return queryset.filter(nurse__user=actor)

        if role == UserRole.ADMIN and getattr(actor, "is_staff", False):
            return queryset

        return queryset.none()

    def get_for_actor(self, *, actor: object, note_id: int) -> VisitNote:
        """Return a single visit note visible to an actor."""
        return get_object_or_404(self.for_actor(actor), id=note_id)
