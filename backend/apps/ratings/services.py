"""Rating service layer."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from apps.accounts.models import UserRole
from apps.audit_logs.services.audit import AuditLogService
from apps.nurses.services.reputation import NurseReputationService
from apps.ratings.models import Rating
from apps.requests.models import CareRequest, CareRequestStatus


class RatingService:
    """Create ratings and refresh nurse reputation signals."""

    def __init__(
        self,
        *,
        audit_service: AuditLogService | None = None,
        reputation_service: NurseReputationService | None = None,
    ) -> None:
        self.audit_service = audit_service or AuditLogService()
        self.reputation_service = reputation_service or NurseReputationService()

    @transaction.atomic
    def create(
        self,
        *,
        actor: object,
        data: dict[str, Any],
        ip_address: str | None,
    ) -> Rating:
        """Create one patient rating for a completed assigned care request."""
        if getattr(actor, "role", None) != UserRole.PATIENT:
            raise PermissionError("Only patients can submit ratings.")

        care_request = get_object_or_404(
            CareRequest.objects.select_for_update(of=("self",)).select_related(
                "patient",
                "assigned_nurse",
            ),
            id=data["care_request_id"],
            is_deleted=False,
        )
        if care_request.patient.user_id != actor.id:
            raise PermissionError("You can rate only your own completed requests.")
        if care_request.status != CareRequestStatus.COMPLETED:
            raise ValueError("Only completed requests can be rated.")
        if care_request.assigned_nurse_id is None:
            raise ValueError("Completed request has no assigned nurse to rate.")
        if Rating.objects.filter(care_request=care_request, is_deleted=False).exists():
            raise ValueError("This request has already been rated.")

        rating = Rating.objects.create(
            patient=care_request.patient,
            nurse=care_request.assigned_nurse,
            care_request=care_request,
            rating=data["rating"],
            comment=data.get("comment", ""),
        )
        self._refresh_nurse_rating(rating)
        self.audit_service.record(
            actor=actor,
            action="RATING_CREATED",
            resource="Rating",
            resource_id=rating.id,
            ip_address=ip_address,
            metadata={
                "care_request_id": care_request.id,
                "nurse_id": rating.nurse_id,
                "rating": rating.rating,
            },
        )
        return rating

    def _refresh_nurse_rating(self, rating: Rating) -> None:
        """Update nurse average rating and reputation after a new rating."""
        average = Rating.objects.filter(nurse=rating.nurse, is_deleted=False).aggregate(
            average=Avg("rating")
        )["average"]
        rating.nurse.rating = Decimal(str(average or 0)).quantize(Decimal("0.01"))
        rating.nurse.save(update_fields=["rating", "updated_at"])
        self.reputation_service.recalculate(nurse=rating.nurse)
