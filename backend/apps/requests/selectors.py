"""Optimized care request selectors."""

from __future__ import annotations

from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404

from apps.accounts.models import UserRole
from apps.requests.models import CareRequest, RequestOfferStatus


class CareRequestSelector:
    """Read care requests using role-aware query boundaries."""

    def base_queryset(self) -> QuerySet[CareRequest]:
        """Return care requests with related data needed by serializers."""
        return (
            CareRequest.objects.select_related(
                "patient",
                "patient__user",
                "dependent",
                "assigned_nurse",
                "assigned_nurse__user",
            )
            .filter(is_deleted=False)
            .order_by("-created_at")
        )

    def for_actor(self, actor: object) -> QuerySet[CareRequest]:
        """Return requests visible to an authenticated actor."""
        role = getattr(actor, "role", None)
        queryset = self.base_queryset()

        if role == UserRole.PATIENT:
            return queryset.filter(patient__user=actor)

        if role == UserRole.NURSE:
            return queryset.filter(
                Q(assigned_nurse__user=actor)
                | Q(
                    offers__nurse__user=actor,
                    offers__status=RequestOfferStatus.OFFERED,
                )
            ).distinct()

        if role == UserRole.ADMIN and getattr(actor, "is_staff", False):
            return queryset

        return queryset.none()

    def get_for_actor(self, *, actor: object, request_id: int) -> CareRequest:
        """Return a single request visible to an actor."""
        return get_object_or_404(self.for_actor(actor), id=request_id)

    def get_for_update(self, *, request_id: int) -> CareRequest:
        """Return a locked care request row for state transitions."""
        return get_object_or_404(
            self.base_queryset().select_for_update(of=("self",)),
            id=request_id,
        )
